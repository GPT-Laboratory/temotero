from dotenv import load_dotenv
import os
import logging
import json

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_BASE_URL_EMBED = os.getenv("OLLAMA_BASE_URL_EMBED", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "snowflake-arctic-embed2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Various configurations
#CHUNK_SIZE = int(os.getenv("CHUNK_SIZE_CHARACTERS"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE_TOKENS", 128))
CHUNK_SEPARATOR = " "
FILE_CHUNK_SEPARATOR="   chunk_"
CHUNK_COUNT_SEPARATOR="-of-"
CHUNK_NAMING_TEMPLATE="{filename}"+FILE_CHUNK_SEPARATOR+"{index}"+CHUNK_COUNT_SEPARATOR+"{total_chunks}"
FILE_SUFFIX = os.getenv("FILE_SUFFIX")
EXAMPLE_QUERY = os.getenv("EXAMPLE_QUERY", "This is an example query")
VERSION = os.getenv("VERSION")
PAGE_SEPARATOR = "\n\n\n\n"

# Assistant related prompt construction
ASSISTANT_PROMPT_PATTERN=os.getenv("ASSISTANT_PROMPT_PATTERN")
__ASSISTANT_INSTRUCTIONS_TASK=os.getenv("ASSISTANT_INSTRUCTIONS_TASK")
__ASSISTANT_INSTRUCTIONS_STRUCTURE=os.getenv("ASSISTANT_INSTRUCTIONS_STRUCTURE")
ASSISTANT_INSTRUCTIONS=os.getenv("ASSISTANT_INSTRUCTIONS", "").format(task=__ASSISTANT_INSTRUCTIONS_TASK, structure=__ASSISTANT_INSTRUCTIONS_STRUCTURE)
ASSISTANT_CONTEXT_PATTERN=os.getenv("ASSISTANT_CONTEXT_PATTERN")
__ASSISTANT_QUERY_STOPWORD=os.getenv("ASSISTANT_QUERY_STOPWORD", "")
__ASSISTANT_RESPONSE_STOPWORD=os.getenv("ASSISTANT_RESPONSE_STOPWORD", "")
ASSISTANT_QUERY_PATTERN=__ASSISTANT_QUERY_STOPWORD+': {query}'
ASSISTANT_RESPONSE_PATTERN=__ASSISTANT_RESPONSE_STOPWORD+":"

# Ollama settings
OLLAMA_LLM_OPTIONS = json.loads(os.getenv("OLLAMA_LLM_OPTIONS", "{'max_tokens': 128}"))
# set stop words
OLLAMA_LLM_OPTIONS["stop"] = ["\n"+__ASSISTANT_QUERY_STOPWORD, "\n"+__ASSISTANT_RESPONSE_STOPWORD]

# Logger settings
__LOG_FORMAT="%(levelname)s\t[%(asctime)s] %(name)s - %(message)s"
__LOG_DATE_FORMAT="%Y-%m-%d %H:%M:%S"

# Setup logger facility
def Logger(verbose):
    verbosity = None
    should_filter = True

    if verbose == 0:
        verbosity = logging.WARNING
    elif verbose == 1:
        verbosity = logging.INFO
        logging.getLogger("httpx").disabled = True
    elif verbose == 2:
        verbosity = logging.INFO
    elif verbose == 3:
        verbosity = logging.DEBUG
    elif verbose == 4:
        verbosity = logging.NOTSET
        # this level of NOTSET will filter httpcore and some other friends
    else:
        verbosity = logging.NOTSET
        should_filter = False
        # this level of NOTSET will not filter anything 
    logging.basicConfig(
        format=__LOG_FORMAT,
        datefmt=__LOG_DATE_FORMAT,
        level=verbosity
    )
    if should_filter:
        logging.getLogger("httpcore.connection").disabled = True
        logging.getLogger("httpcore.http11").disabled = True
        logging.getLogger("watchdog.observers.inotify_buffer").disabled = True

#
# stuff below are not in .env, move if really needed

# File name structure for FAISS data
EMBEDDINGS_FILE = 'embeddings.npy'
FILE_NAMES_FILE = 'file_names.npy'
FAISS_INDEX_FILE = 'faiss.index'
