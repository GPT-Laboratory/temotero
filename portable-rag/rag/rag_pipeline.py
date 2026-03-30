
from .document_loader import DocumentLoader, SPLIT_STRATEGY
from .vector_store import VectorStore
from app.embeddings import get_embedding, get_embeddings
from app.llm import get_llm_response

from typing import List
import os
import json

import logging
logger = logging.getLogger(__name__)

from app.config import ASSISTANT_CONTEXT_PATTERN, ASSISTANT_PROMPT_PATTERN, ASSISTANT_QUERY_PATTERN
from app.config import FAISS_INDEX_FILE, FILE_NAMES_FILE

class RAGPipeline:
    def __init__(self, datapath: str, originalspath: str):
        self.datapath = datapath
        self.originalspath = originalspath
        self.vector_store = None
        self.ready = False
        self.loader = DocumentLoader(SPLIT_STRATEGY["PAGINATE"])
        if os.path.exists(f"{self.datapath}/{FAISS_INDEX_FILE}"):
            index_file=f"{self.datapath}/{FAISS_INDEX_FILE}"
            document_file=f"{self.datapath}/{FILE_NAMES_FILE}"
            self.vector_store = VectorStore.fromfile(index_file, document_file)
            self.ready = True
            logger.info("FAISS index read from file successfully.")
        else:
            logger.warning("No index files found from '%s', make sure to initialize FAISS index before use.", datapath)
    
    def is_ready(self) -> bool:
        return self.ready

    async def __make_provisional_embed_query__(self) -> int:
        """Makes a provisional dummy embed query to determine dimensions of a query"""
        dummy_embedding = await get_embedding("")
        embed_dimensions = len(dummy_embedding[0])
        return embed_dimensions
    
    def __check_index_compatibility__(self, embed_dimensions: int):
        if self.is_ready(): # ie., a previous index is being used, make sure dimensions match
            if self.vector_store.dimension != embed_dimensions:
                logger.critical("Dimensions of the index (%d) and the current embed model (%d) do not match. Document embedding shall not proceed.", self.vector_store.dimension, embed_dimensions)
                return False
        else: # ie., FAISS index was not yet created, make new with correct dimension
            self.vector_store = VectorStore.fromdimension(embed_dimensions)
            self.ready = True
            logger.info("FAISS index initialized with dimension=%d", self.vector_store.dimension)
        return True # index should be fine

    async def add_documents(self):
        documents, filenames = self.loader.load_documents(self.originalspath)
        logger.info("Amount of applicable documents in path '%s': %d", self.originalspath, len(documents))

        embed_dimensions = await self.__make_provisional_embed_query__()
        if not self.__check_index_compatibility__(embed_dimensions):
            # return immediately if the index is not compatible
            return (self.vector_store.documents, self.vector_store.index)

        for document, filename in zip(documents, filenames):
            chunks, chunk_names = self.loader.split_document(document, filename)
            if len(chunks) < 1:
                logger.warning("File '%s' had zero chunks, skipping...", filename)
                continue
            embeddings = await get_embeddings(chunks) # lists can be queried as batch
            
            for i in range(len(embeddings)):
                self.vector_store.add_document(chunk_names[i], embeddings[i])
            logger.info("Document with %d chunks added.", len(chunks))

        return (self.vector_store.documents, self.vector_store.index)

    async def query(self, user_query: str, top_k: int = 5):
        """ User query to embedding to top-k to context-query to answer.
            Assumes that embedding dimensions of index and query match.
            1. Step 1) Make user query
            2. Step 2) Embed query using a embedding model
            3. Step 3) Retrieve top-k relevant documents
            4. Step 4) Construct User Query + Similar Docs for LLM query
            5. Step 5) Generate answer based on query
        """

        # Step 2) Embed query using an embedding model
        logger.debug("Query (embed):\n%s", user_query)
        embedding = await get_embedding(prompt=user_query) # defaul model (from .env)
        logger.debug("Embedding dimensions: %d", len(embedding[0]))
        logger.log(logging.DEBUG-2, embedding[0])

        # Step 3) Retrieve top-k relevant documents/chunks
        distances, indices = self.vector_store.search(embedding, top_k)
        similar_chunks = self.vector_store.search_similar_chunks(distances=distances, indices=indices)
        logger.debug("Similarities: %s", json.dumps(similar_chunks, indent=2))

        # Step 4) Construct User Query + Similar Docs for LLM query
        context = self.__build_query_context__(similar_chunks=similar_chunks)
        query = self.__build_llm_query__(user_query=user_query, context=context)
        logger.log(logging.DEBUG-1, "Query (embed+LLM):\n%s", query)

        # Step 5) Generate answer based on query
        return await self.__generate_answer__(query)

    def __build_query_context__(self, similar_chunks) -> str:
        """ Make a query for LLM
            - Step 4.2) Construct User Query + **Similar Docs** for LLM query
        """ 
        if len(similar_chunks) < 1:
            logger.critical("Similar content and context is missing. There will be very few reasons to proceed.")
        context = { "context": [] }
        for fname, dist in similar_chunks:
            context["context"].append({ "source": fname, "similarity": float(dist), "chunk": self.loader.load_document_chunk(self.originalspath, fname) })
        return context

    def __build_llm_query__(self, user_query: str, context: dict) -> str:
        """ Make a query for LLM
            - Step 4.1) **Construct User Query** + Similar Docs for LLM query
        """ 
        prompt = (
            ASSISTANT_PROMPT_PATTERN.format(
                #instructions="",#ASSISTANT_INSTRUCTIONS are moved to system prompt
                context=ASSISTANT_CONTEXT_PATTERN.format(context=json.dumps(context, indent=2)),
                query=ASSISTANT_QUERY_PATTERN.format(query=user_query),
                response="",#ASSISTANT_RESPONSE_PATTERN
            )
        )
        return prompt
    
    async def __generate_answer__(self, prompt: str) -> json:
        """ Step 5) Generate answer based on query
        """
        json = await get_llm_response(prompt=prompt)
        str = json.model_dump_json(indent=2, exclude="context") # strip context field for debug logging
        logger.log(logging.DEBUG-1, str)
        
        return json
    
    async def explain_query(self, prompt: str) -> str:
        return await self.__generate_answer__(prompt=prompt)

    def store_index(self):
        index_file=f"{self.datapath}/{FAISS_INDEX_FILE}"
        document_file=f"{self.datapath}/{FILE_NAMES_FILE}"
        self.vector_store.store_index(index_file, document_file)
        logger.info("Vector storage saved to disk (%s, %s)", index_file, document_file)
