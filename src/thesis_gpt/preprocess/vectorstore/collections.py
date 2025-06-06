import weaviate
import weaviate.classes as wvc
from beartype import beartype
from weaviate.collections import Collection


@beartype
class ThesisCollection:
    """
    A class to manage a Weaviate collection for storing Thesis chunks.
    This class handles the creation of the collection, insertion of chunks, and querying by chapter
    title.
    Args:
        client (weaviate.Client): The Weaviate client instance.
        name (str): The name of the collection.
        reset (bool): If True, resets the collection by deleting it if it exists. Defaults to False.
    """

    def __init__(
        self, client: weaviate.client.WeaviateClient, name: str, reset: bool = False
    ):
        self.client = client
        self.name = name

        if reset and client.collections.exists(name):
            client.collections.delete(name)

        self.collection = self._create_collection()

    def _create_collection(self) -> Collection:
        """
        Create a Weaviate collection with predefined properties and configurations.
        Returns:
            weaviate.Collection: The created collection instance.
        """
        return self.client.collections.create(
            name=self.name,
            properties=[
                wvc.config.Property(name="chunk", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="chapter", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="section", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(
                    name="subsection", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="subsubsection", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="paragraph", data_type=wvc.config.DataType.TEXT
                ),
                wvc.config.Property(
                    name="chunk_index", data_type=wvc.config.DataType.INT
                ),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
            generative_config=wvc.config.Configure.Generative.openai(),
        )

    def init_chunk(
        self,
        chunk: str,
        chapter: str | None,
        chunk_index: int,
        section: str | None = None,
        subsection: str | None = None,
        subsubsection: str | None = None,
        paragraph: str | None = None,
    ) -> wvc.data.DataObject:
        """
        Create a chunk with the specified properties and return a DataObject.
        Args:
            chunk (str): The text content of the chunk.
            chapter (str): The title of the chapter.
            section (str, optional): The title of the section. Defaults to None.
            subsection (str, optional): The title of the subsection. Defaults to None.
            subsubsection (str, optional): The title of the subsubsection. Defaults to None.
            paragraph (str, optional): The title of the paragraph. Defaults to None.
            chunk_index (int): The index of the chunk in its chapter.
        Returns:
            wvc.data.DataObject: A DataObject representing the chunk with its properties.
        """
        data_properties = {
            "chunk": chunk,
            "chapter": chapter,
            "section": section,
            "subsection": subsection,
            "subsubsection": subsubsection,
            "paragraph": paragraph,
            "chunk_index": chunk_index,
        }
        data_object = wvc.data.DataObject(properties=data_properties)
        return data_object

    def query_by_chapter(self, chapter_title: str):
        return self.collection.query.near_text(
            query="chunk about " + chapter_title, limit=5
        )
