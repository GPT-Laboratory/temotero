import faiss
import numpy as np
import numpy.typing as npt
from typing import List

import logging
logger = logging.getLogger(__name__)

class VectorStore:

    def __init__(self, index: faiss.IndexFlatL2, documents: List[str]):
        self.index = index
        self.documents = documents
        self.dimension = index.d

    @classmethod
    def fromfile(cls, faiss_index_filename: str, documents_filename: str):
        """ Index from a pre-existing file """
        index = faiss.read_index(faiss_index_filename)
        document_array=np.load(documents_filename).tolist()
        return cls(index, document_array)
        # these are not utilized?
        # embeddings = np.load(EMBEDDINGS_FILE)
        # embeddings = normalize_embeddings(embeddings)

    @classmethod
    def fromdimension(cls, dimension: int):
        "Initialize using dimension"
        return cls(faiss.IndexFlatL2(dimension), [])

    def add_document(self, document: str, embedding: List[float]):
        embedding_to_index = np.array([embedding], dtype=np.float32)
        embedding_to_index = self.__normalize_query_embedding__(embedding_to_index)
        self.documents.append(document)
        self.index.add(embedding_to_index)

    def search(self, embedding: List[float], top_k: int = 5) -> list[(str, float)]:
        query = np.array(embedding).astype("float32") # make sure embedded query vector is of type f32
        query = self.__normalize_query_embedding__(query) # normalize

        if self.index.d != query.size:
            logger.critical("Index and query embedding dimension do not match (%d!=%d). Search can not proceed.", self.index.d, query.size)
            return [[]], [[]]
        
        distances, indices = self.index.search(query, k=top_k)
        return distances, indices

    def search_similar_chunks(self, distances, indices, distance_threshold: float = 2.0):
        """ Returns context tuple (document, distance) """
        # find similar context
        results = []
        for idx, i in enumerate(indices[0]):
            if distances[0][idx] < distance_threshold and i != -1:
                results.append((self.documents[i], float(distances[0][idx])))
        return results # return context tuple (document, distance)

    def store_index(self, faiss_index_filename: str, documents_filename: str):
        # NB! embeddings are not separately stored, just documents and index
        # Convert document file names to NumPy arrays
        documents_numpy = np.array(self.documents)
        # Save file names
        np.save(documents_filename, documents_numpy)
        # Save FAISS index
        faiss.write_index(self.index, faiss_index_filename)

    def __normalize_query_embedding__(self, query_embedding: npt.ArrayLike):
        """Normalize each query embedding before working on them"""
        return query_embedding / np.linalg.norm(query_embedding)
