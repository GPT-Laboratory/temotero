from .ollama_client import OllamaClient
from .config import EMBEDDING_MODEL

from typing import List

client = OllamaClient()

async def get_embedding(prompt: str, model: str = EMBEDDING_MODEL) -> List[float]:
    result = await client.generate_embedding(prompt=prompt, model=model)
    return result.get("embeddings")

async def get_embeddings(prompts: List[str], model: str = EMBEDDING_MODEL) -> List[List[float]]:
    result = await client.generate_embedding_batch(prompts=prompts, model=model)
    return result.get("embeddings")
