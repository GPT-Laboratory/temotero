import os
import argparse

from rag.rag_pipeline import RAGPipeline
from webui.webui import WebUI

import logging
from app.config import Logger, EMBEDDING_MODEL, LLM_MODEL, EXAMPLE_QUERY, VERSION

def arguments():
    # Initialize parser
    parser = argparse.ArgumentParser(description = "This is a RAG implementation with portability in mind. It is highly configurable, and for example can be instructed to utilize different Ollama API endpoints for LLM and Embedding tasks.")

    parser.add_argument("-s", "--servermode", help = "Runs the program in HTTP/REST mode.", action='store_true')
    parser.add_argument("-v", "--verbose", help = "Increases verbosity", action='count', dest='log_level', default=1)
    parser.add_argument("--quiet", help = "Set verbosity to minimum", action='store_true')
    parser.add_argument("--example", help = "Makes a predetermined set of operations as an example and to test the pipeline.", action='store_true')
    parser.add_argument("--explain", help = "Makes the query directly to generative model, for debugging purposes.", action='store_true')
    parser.add_argument("--overwrite", help = "Overwrites any and all files without further questions", action='store_true')

    group1 = parser.add_argument_group("Documents, indexing, and (re)embedding")
    group1.add_argument("-i", "--indexpath", help = "Specifies the path for index files (embeddings, faiss, et al.)", required=True)
    group1.add_argument("-o", "--originalspath", help = "Specifies the path for the original files used for embedding", required=True)
    group1.add_argument("-e", "--embed", help = "(Re)Embeds all suitable documents in ORIGINALSPATH", 
    action='store_true')
    group1.add_argument("-q", "--query", help = "An user query, flag may be used multiple times.", nargs=argparse.ONE_OR_MORE, action='append')
    return parser, parser.parse_args()

parser, args = arguments()
Logger(0 if args.quiet == True else args.log_level)
logger = logging.getLogger("PortableRAG")

# Check for argument sanity & requirements
if not os.path.isdir(args.indexpath):
    parser.error(f"'{args.indexpath}' is not a valid directory.")
if args.originalspath and not os.path.isdir(args.originalspath):
    parser.error(f"'{args.originalspath}' is not a valid directory.")
if args.embed and not args.originalspath:
    parser.error("Arguments -e and -o are mutually inclusive")
if args.embed and args.servermode:
    parser.error("Arguments -e and -s are mutually exclusive")


def embed_all_files(rag_pipeline: RAGPipeline):
    import asyncio
    loop = asyncio.new_event_loop()
    retval = loop.run_until_complete(
        rag_pipeline.add_documents()
    )
    logger.info(f"Document chunks in the index {len(retval[0])}")

def do_query(rag_pipeline: RAGPipeline, user_query: str = EXAMPLE_QUERY):
    if rag_pipeline.is_ready():
        import asyncio
        logger.info("RAG Pipeline is ready")
        loop = asyncio.new_event_loop()
        retval = None
        if args.explain:
            retval = loop.run_until_complete(
                rag_pipeline.explain_query(user_query)
            )
        else:
            retval = loop.run_until_complete(
                # Step 1) Make user query
                rag_pipeline.query(user_query)
            )
        logger.info("Question:\n\t%s", user_query)
        logger.info("Response:\n\t%s", retval.response)
        return retval
    else:
        logger.warning("RAG Pipeline was not properly set")

def main():
    logger.info(f"Preparing PortableRAG (v{VERSION}) with\nEmbed model: {EMBEDDING_MODEL}\nGenerative model: {LLM_MODEL}")
    rag_pipeline = RAGPipeline(datapath=args.indexpath, originalspath=args.originalspath) # initializes pipeline, and reads index if available

    if args.servermode:
        if not rag_pipeline.is_ready():
            logger.critical("RAG Pipeline was not properly set. Server mode is unable to continue...")
            exit(-1)
        logger.info("Running in server mode")
        ui = WebUI(pipeline=rag_pipeline,
                   title="<RAG Agent>",
                   placeholder="<Enter search query>",
                   instructions="""<Introduction placeholder>

                   <Instruction placeholder>
                   
    Version: {version}
    GenAI model: {model}
    Embed model: {embed}""".format(model=LLM_MODEL, embed=EMBEDDING_MODEL, version=VERSION))
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            asyncio.run(ui.rootpage())
        except KeyboardInterrupt:
            pass
        finally:
            logger.debug("Closing Loop")
            loop.close()
    elif args.embed and args.example:
        logger.info("Embedding files and running an example")
        embed_all_files(rag_pipeline)
        do_query(rag_pipeline)
    elif args.example:
        logger.info("Running an example")
        do_query(rag_pipeline)
    elif args.embed:
        logger.info("Embedding files on %s", args.originalspath)
        embed_all_files(rag_pipeline)
        if args.overwrite:
            rag_pipeline.store_index()
    elif args.query:
        for user_query in args.query: # iterate thru each command line query
            parsed_query = " ".join(user_query).strip()
            do_query(rag_pipeline, parsed_query)
    else:
        logger.warning("The application did not do anything, please recheck arguments.")

if __name__ == "__main__":
    main()
