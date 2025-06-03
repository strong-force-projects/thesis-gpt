import logging
import os

import weaviate
from beartype import beartype
from dotenv import load_dotenv
from weaviate.classes.init import Auth

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Load environment variables from .env file
# This is necessary to access the Weaviate URL and API key.
load_dotenv()


@beartype
class WeaviateDB:
    def __init__(self, headers: dict = None):
        """
        Initialize the WeaviateDB client with the provided headers.
        Args:
            headers (dict, optional): Additional headers to include in the connection request,
            (e.g. OpenAI API key).
        """
        self.client = self._connect_to_cloud(
            cluster_url=os.environ["WEAVIATE_URL"],
            auth_credentials=Auth.api_key(os.environ["WEAVIATE_API_KEY"]),
            headers=headers,
        )
        assert self.client.is_ready(), "Weaviate client is not ready."

    def _connect_to_cloud(
        self,
        cluster_url: str,
        auth_credentials: weaviate.auth._APIKey,
        headers: dict = None,
    ) -> weaviate.client.WeaviateClient:
        """
        Connect to Weaviate Cloud using the provided cluster URL and authentication credentials.

        Args:
            cluster_url (str): The URL of the Weaviate Cloud cluster.
            auth_credentials (Auth): Authentication credentials for accessing the cluster.
            headers (dict, optional): Additional headers to include in the connection request,
            (e.g. OpenAI API key).

        Returns:
            weaviate.Client: A Weaviate client instance connected to the specified cluster.
        """
        return weaviate.connect_to_weaviate_cloud(
            cluster_url=cluster_url,
            auth_credentials=auth_credentials,
            headers=headers,
        )

    def close(self):
        self.client.close()
