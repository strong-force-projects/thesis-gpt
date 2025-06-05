import logging
import os
from dataclasses import dataclass
from beartype import beartype

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
        Additionally, you can use the context provided in this system prompt to help answer the question.
        The PhD thesis is titled Advances in Machine Learning for Sensor Data with Applications in Smart Agriculture and Beyond.
        Only use information present in the text. If the answer is not clearly present in the text, say so and ask the user to rephrase the question and elaborate.
        The text may contain latex formatting, which you should clean up before using it in your response into a format suitable to show in a Streamlit app.
        
        User Question: "{self.query}"

        Rules:
        - If the question involves images or figures, state that images are not available and describe only captions if present.
        - If the question is unrelated to the thesis, clearly say it cannot be answered.
        """

@beartype
class ThesisRetriever:
    """
    A class to retrieve information from a thesis using Weaviate as a vector store.
    It allows querying the thesis content and retrieving relevant chunks based on the query.
    These chunks are then used to generate a response that summarizes the relevant information.
    """

    @staticmethod
    def retrieve(query: str):
        """
        Retrieve relevant chunks from the thesis based on the provided query.
        Args:
            query (str): The query string to search for in the thesis.
        Returns:
            str: The generated response based on the retrieved chunks.
        """
        with WeaviateDB(
            headers={"X-Openai-Api-Key": os.getenv("OPENAI_APIKEY")}
        ) as db_client:
            collection = db_client.client.collections.get("thesis_chunks")
            response = collection.generate.near_text(
                query=query,
                limit=5,
                grouped_task=ThesisPrompt(query).system,
                return_properties=[
                    "chapter",
                    "section",
                    "subsection",
                    "subsubsection",
                    "paragraph",
                ],
            )
            logger.info(f"Querying Weaviate with: {query}")
        return response.generated
