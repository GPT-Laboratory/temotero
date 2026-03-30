from .ollama_client import OllamaClient

from .config import LLM_MODEL, ASSISTANT_INSTRUCTIONS

from ollama import GenerateResponse

import logging
logger = logging.getLogger(__name__)

client = OllamaClient()

async def get_llm_response(prompt: str, system: str = ASSISTANT_INSTRUCTIONS, model: str = LLM_MODEL) -> GenerateResponse:
    logger.log(logging.DEBUG-2, "System prompt:\n%s", system)
    result = await client.generate_response(system=system, prompt=prompt, model=model)
    return result
