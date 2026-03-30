import os
from typing import List

from app.config import CHUNK_SIZE, CHUNK_SEPARATOR, CHUNK_NAMING_TEMPLATE, FILE_CHUNK_SEPARATOR, CHUNK_COUNT_SEPARATOR, FILE_SUFFIX
from app.config import PAGE_SEPARATOR

SPLIT_STRATEGY = {
    "PAGINATE": "paginate",
    "CHUNK": "chunk"
}

class DocumentLoader:
    def __init__(self, split_strategy = SPLIT_STRATEGY["PAGINATE"]):
        self.split_strategy = split_strategy

    def load_documents(self, path: str, suffix: tuple[str, ...] = (FILE_SUFFIX)):
        documents = []
        filenames = os.listdir(path)
        for filename in filenames:
            if filename.endswith(suffix):
                with open(os.path.join(path, filename), 'r') as f:
                    documents.append(f.read())
        return (documents, filenames)

    def split_document(self, document: str, filename: str) -> List[str]:
        if self.split_strategy == SPLIT_STRATEGY["CHUNK"]:
            return self.__chunk_document__(document, filename)
        elif self.split_strategy == SPLIT_STRATEGY["PAGINATE"]:
            return self.__paginate_document__(document, filename)
        else:
            raise NotImplementedError
    
    def __chunk_document__(self, document: str, filename: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """ Split document into chunks as specified in chuck_size (characters) """
        chunks = self.__splitter__(document, chunk_size)
        chunkNames = [CHUNK_NAMING_TEMPLATE.format(filename=filename, index=i+1, total_chunks=len(chunks)) for i in range(len(chunks))]
        return (chunks, chunkNames)

    def __paginate_document__(self, document: str, filename: str) -> List[str]:
        """ Split document into chunks by using paging strategy """
        chunks = document.split(PAGE_SEPARATOR)
        chunkNames = [CHUNK_NAMING_TEMPLATE.format(filename=filename, index=i+1, total_chunks=len(chunks)) for i in range(len(chunks))]
        return (chunks, chunkNames)

    def load_document_chunk(self, path: str, filename_pattern: str, chunk_size: int = CHUNK_SIZE) -> str:
        filename, chunk = self.__filename_chunk_parser__(filename_pattern)
        document = None
        if filename:
            with open(os.path.join(path, filename), 'r') as f:
                document = f.read()
        if(self.split_strategy == SPLIT_STRATEGY["CHUNK"]):
            return self.__splitter__(document, chunk_size, chunk)[-1]
        elif(self.split_strategy == SPLIT_STRATEGY["PAGINATE"]):
            pages = document.split(PAGE_SEPARATOR)
            return pages[chunk]
        else:
            raise NotImplementedError

    def __filename_chunk_parser__(self, filename_pattern: str) -> tuple[str, int]:
        parts = filename_pattern.split(FILE_CHUNK_SEPARATOR)
        file_part = parts[0]
        chunk_part = int(parts[-1].split(CHUNK_COUNT_SEPARATOR)[0]) - 1 # adjust for zero index
        return file_part, chunk_part

    def __splitter__(self, document: str, chunk_size: int = CHUNK_SIZE, chunk: int = -1) -> List[str]:
        words = document.split(CHUNK_SEPARATOR)
        range_start = chunk*chunk_size if chunk >= 0 else 0
        range_stop = range_start+chunk_size if chunk >= 0 else len(words)
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(range_start, range_stop, chunk_size)]
        return chunks
