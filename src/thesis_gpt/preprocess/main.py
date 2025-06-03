import argparse
import logging
import os

from dotenv import load_dotenv

from thesis_gpt.preprocess.parsers.latex_parser import LatexChunker, LatexDocParser
from thesis_gpt.preprocess.parsers.utils import validate_latex_path
from thesis_gpt.preprocess.vectorstore.collections import ThesisCollection
from thesis_gpt.preprocess.vectorstore.weaviate_client import WeaviateDB

logger = logging.getLogger(__name__)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Parse LaTeX documents and convert to Markdown."
    )
    argparser.add_argument(
        "path",
        type=str,
        help="Path to a LaTeX file or directory containing LaTeX files.",
    )
    args = argparser.parse_args()

    validate_latex_path(args.path)
    parser = LatexDocParser(args.path)
    markdown_text = parser.parse()
    chunker = LatexChunker()
    docs = chunker.chunk(markdown_text)

    logger.info(f"Parsed {len(docs)} chunks from the LaTeX document.")

    db_client = WeaviateDB(headers={"X-Openai-Api-Key": os.getenv("OPENAI_APIKEY")})
    try:
        thesis_data = ThesisCollection(
            db_client.client, name="thesis_chunks", reset=True
        )
        chunks_list = list()
        with thesis_data.collection.batch.fixed_size(batch_size=50) as batch:
            for i, chunk in enumerate(docs):
                data_properties = {
                    "chunk": chunk.page_content,
                    "chapter": chunk.metadata.get("chapter"),
                    "section": chunk.metadata.get("section"),
                    "subsection": chunk.metadata.get("subsection"),
                    "subsubsection": chunk.metadata.get("subsubsection"),
                    "paragraph": chunk.metadata.get("paragraph"),
                    "chunk_index": i,
                }
                batch.add_object(properties=data_properties)
        db_client.close()
    except:
        logger.exception("An error occurred while processing the LaTeX document")
        db_client.close()
