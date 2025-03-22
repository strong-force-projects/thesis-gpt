import weaviate
from weaviate.classes.config import Property, DataType, Configure


class WeaviateDB:
    def __init__(self):
        self.client = weaviate.connect_to_local()
        if not self.client.is_ready():
            raise ConnectionError("Failed to connect to local Weaviate instance")
        self.client.collections.create(
            name="ThesisDocument",
            description="The complete, unchunked, thesis document",
            properties=[
                Property(
                    name="main_text", data_type=DataType.TEXT, skip_vectorization=True
                )
            ],
        )
        self.client.collections.create(
            name="Chunks",
            description="Thesis Chunks",
            properties=[
                Property(
                    name="section_header",
                    data_type=DataType.TEXT,
                    skip_vectorization=True,
                ),
                Property(
                    name="chunk_text", data_type=DataType.TEXT, skip_vectorization=False
                ),
            ],
            vectorizer_config=[
                Configure.NamedVectors.text2vec_openai(
                    name="vectorizer_openai_1",
                    source_properties=["chunk_text"],
                    model="text-embedding-3-small",
                    dimensions=512,
                )
            ],
        )

    def close(self):
        self.client.close()
