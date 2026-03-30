import ollama
from typing import List

from .config import OLLAMA_BASE_URL, OLLAMA_BASE_URL_EMBED, OPENAI_API_KEY, OLLAMA_LLM_OPTIONS

AUTHORIZATION="Authorization"
BEARER_TOKEN="Bearer {token}"

class OllamaClient:
    def __init__(self,
                 base_url: str = OLLAMA_BASE_URL,
                 base_url_embed: str = OLLAMA_BASE_URL_EMBED,
                 bearer: str = OPENAI_API_KEY):
        self.base_url = base_url
        self.base_url_embed = base_url_embed
        self.bearer = bearer
    
    def __get_client(self, base_url):
        return ollama.AsyncClient(
            host=base_url,
            headers={AUTHORIZATION: BEARER_TOKEN.format(token=self.bearer)}
        )

    async def generate_embedding(self, prompt: str, model: str):
        #simply pass through to batch handler
        return await self.generate_embedding_batch([prompt], model)
    
    async def generate_embedding_batch(self, prompts: List[str], model: str):
        client = self.__get_client(self.base_url_embed)
        response = await client.embed(model=model, input=prompts)
        return response

    async def generate_response(self, system: str, prompt: str, model: str) -> ollama.GenerateResponse:
        client = self.__get_client(self.base_url)
        response = await client.generate(
            model=model, prompt=prompt, system=system,
            options=OLLAMA_LLM_OPTIONS
        )
        return response
