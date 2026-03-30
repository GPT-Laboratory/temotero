# PortableRAG

## Preconditions
1. Python
2. Python venv 
   * `python -m venv venv`
   * `source venv/bin/activate`
3. Python requirements
   * `pip install -r requirements.txt`
5. Setup .env
   * Ollama access (OLLAMA_BASE_URL and OPENAI_API_KEY)
   * Embed model (EMBEDDING_MODEL)
   * Generative model (LLM_MODEL)
   * Chunk size selection (CHUNK_SIZE_TOKENS)
6. Source documents converted to text files (./data/texts/*) `-o/--originalspath`
7. Embedded source text documents as FAISS index (./data/index/{embeddings.npy,faiss.index,file_names.npy}) `-i/--indexpath`
   * Changes to source texts require re-embedding (due to additional data)
   * Changes to embed model require re-embedding (due to different embed dimension and/or vocabulary)

## Usage

### Examples

* Minimal query example
  `python main.py -i data/index/ -o data/texts/ --example`
* Embed Files & Query example
  `python main.py -i data/index/ -o data/texts/ -e --example`

#### Actual Pilot Case
1. Create directory structure `mkdir -p data/pilot/{pdf,texts,snowflake-arctic-embed2}`
2. Copy your pdfs to `pdf` directory
3. Copy other text files to `texts` directory
4. PDF-to-Text: `python data/crawler.py -s data/pilot/pdf/ -o data/pilot/texts/`
5. Embed text files: `python main.py -i data/pilot/snowflake-arctic-embed2/ -o data/pilot/texts/ -e -v --overwrite`
   ```INFO	[2025-06-09 14:44:44] PortableRAG - Preparing PortableRAG with
Embed model: snowflake-arctic-embed2
Generative model: llama3.2
WARNING	[2025-06-09 14:44:44] rag.rag_pipeline - No index files found from 'data/pilot/snowflake-arctic-embed2/', make sure to initialize FAISS index before use.
INFO	[2025-06-09 14:44:44] PortableRAG - Embedding files on data/pilot/texts/
INFO	[2025-06-09 14:44:44] rag.rag_pipeline - Amount of applicable documents in path 'data/pilot/texts/': 1
INFO	[2025-06-09 14:44:46] httpx - HTTP Request: POST https://gptlab.rd.tuni.fi/GPT-Lab/resources/GPU-farmi-001/api/embed "HTTP/1.1 200 OK"
INFO	[2025-06-09 14:44:46] rag.rag_pipeline - FAISS index initialized with dimension=1024
INFO	[2025-06-09 14:45:20] httpx - HTTP Request: POST https://gptlab.rd.tuni.fi/GPT-Lab/resources/GPU-farmi-001/api/embed "HTTP/1.1 200 OK"
INFO	[2025-06-09 14:45:25] rag.rag_pipeline - Document with 469 chunks added.
INFO	[2025-06-09 14:45:25] PortableRAG - Document chunks in the index 469
INFO	[2025-06-09 14:45:25] rag.rag_pipeline - Vector storage saved to disk (data/pilot/snowflake-arctic-embed2//faiss.index, data/pilot/snowflake-arctic-embed2//file_names.npy)```
