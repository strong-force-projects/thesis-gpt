import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from thesis_gpt.preprocess.vectorstore.weaviate_client import WeaviateDB

logger = logging.getLogger(__name__)
load_dotenv()


@dataclass
class ThesisPrompt:
    """
    A dataclass to hold the prompt template for querying the thesis.
    It includes the system prompt.
    """

    query: str

    def __post_init__(self):
        self.system = f"""
        You are an academic assistant. Use the following retrieved text fragments from a PhD thesis to answer the question below.
        Only use information present in the text. If the answer is not clearly present in the text, say so and ask the user to rephrase the question and elaborate.

        User Question: "{self.query}"

        Rules:
        - If the question involves images or figures, state that images are not available and describe only captions if present.
        - If the question is unrelated to the thesis, clearly say it cannot be answered.
        """


class ThesisRetriever:
    """
    A class to retrieve information from a thesis using Weaviate as a vector store.
    It allows querying the thesis content and retrieving relevant chunks based on the query.
    These chunks are then used to generate a response that summarizes the relevant information.
    """

    def __init__(self):
        self.db_client = WeaviateDB(
            headers={"X-Openai-Api-Key": os.getenv("OPENAI_APIKEY")}
        )

    def retrieve(self, query: str):
        """
        Retrieve relevant chunks from the thesis based on the provided query.
        Args:
            query (str): The query string to search for in the thesis.
        Returns:
            str: The generated response based on the retrieved chunks.
        """
        collection = self.db_client.client.collections.get("thesis_chunks")
        response = collection.generate.hybrid(
            query=query,
            limit=3,
            grouped_task=ThesisPrompt(query).system,
            return_properties=[
                "chapter",
                "section",
                "subsection",
                "subsubsection",
                "paragraph",
            ],
        )
        self.db_client.close()
        logger.info(f"Querying Weaviate with: {query}")
        return response.generated
