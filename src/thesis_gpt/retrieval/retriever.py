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
        You are an academic assistant helping answer questions based on retrieved text fragments from a PhD thesis.

        Thesis title: "Advances in Machine Learning for Sensor Data with Applications in Smart Agriculture and Beyond"  
        Author: Boje Deforce

        Guidelines:
        1. Use only the retrieved text fragments and provided context to answer the question. Do not use outside knowledge.
        2. If relevant information is clearly missing in the retrieved text, state this clearly and ask the user to rephrase or elaborate. 
        Though, you can use the context to infer missing information but only do so if it is clearly implied in the text.
        3. If LaTeX formatting is present:
        - Convert it to clean Markdown where possible.
        - If conversion is not possible, explain the meaning in plain text or omit purely formatting commands.
        4. If images or figures are referenced:
        - State that images are unavailable.
        - Describe captions if present.
        5. If the retrieved text references different sections of the thesis, try to provide a coherent answer that connects the information.
        6. If the question is too broad or requires summarization, answer the question as best as possible, but suggest the user to ask more specific questions for better answers.

        User Question: "{self.query}"
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
        with WeaviateDB(headers={"X-Openai-Api-Key": os.getenv("OPENAI_APIKEY")}) as db_client:
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
