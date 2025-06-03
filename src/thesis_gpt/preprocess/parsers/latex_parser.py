import re
from pathlib import Path
from typing import List, Union

from beartype import beartype
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter


@beartype
class LatexDocParser:
    """
    Convert LaTeX formatted text to a pseudo-Markdown format and parse it into semantically
    meaningful chunks. This is a hacky conversion that replaces LaTeX sectioning commands with
    Markdown headers as there is no satisfactory LaTeX parser available in Python. It does not
    handle all LaTeX features and is intended for simple documents where sectioning is the primary
    concern.
    """

    def __init__(self, path: Union[str, Path]):
        """
        Args:
            path: A path to a LaTeX file or folder containing LaTeX files.
        """
        self.path = Path(path)
        self.root_path = self.path.parent.resolve()

    def _load_file(self, file_path: Path) -> str:
        """Load the content of a LaTeX file.
        Args:
            file_path: Path to the LaTeX file.
        Returns:
            The content of the LaTeX file as a string.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _resolve_inputs(self, text: str, base_path: Path) -> str:
        """Recursively resolve LaTeX input and include commands.
        Args:
            text: The LaTeX text to process.
            base_path: The base path for resolving relative file paths.
        Returns:
            The processed text with all input and include commands resolved.
        """
        pattern = re.compile(r"\\(?:input|include)\{([^\}]+)\}")
        while match := pattern.search(text):
            relative_path = match.group(1)
            included_file = Path(self.root_path / relative_path).with_suffix(".tex")
            if not included_file.exists():
                raise FileNotFoundError(f"Included file not found: {included_file}")
            included_text = self._load_file(included_file)
            resolved_text = self._resolve_inputs(included_text, included_file.parent)
            text = text[: match.start()] + resolved_text + text[match.end() :]
        return text

    def _convert_to_markdown(self, latex_text: str) -> str:
        """Convert LaTeX text to pseudo-Markdown format.
        Args:
            latex_text: The LaTeX text to convert.
        Returns:
            The converted text in pseudo-Markdown format.
        """
        latex_text = re.sub(r"\\chapter\{(.*?)\}", r"# \1\n\n", latex_text)
        latex_text = re.sub(r"\\section\{(.*?)\}", r"## \1\n\n", latex_text)
        latex_text = re.sub(r"\\subsection\{(.*?)\}", r"### \1\n\n", latex_text)
        latex_text = re.sub(r"\\subsubsection\{(.*?)\}", r"#### \1\n\n", latex_text)
        latex_text = re.sub(r"\\paragraph\{(.*?)\}", r"##### \1\n\n", latex_text)
        return latex_text

    def _clean_latex_text(self, latex_text: str) -> str:
        """Clean up LaTeX text by removing unnecessary commands and formatting.
        Args:
            latex_text: The LaTeX text to clean.
        Returns:
            The cleaned LaTeX text.
        """
        # Remove comments
        latex_text = re.sub(r"%.+", "", latex_text)
        # Remove labels
        latex_text = re.sub(r"\\label\{.*?\}", "", latex_text)
        return latex_text

    def parse(self) -> str:
        """
        Parses the main LaTeX file and all included files, returning a combined pseudo-Markdown string.
        """
        if not self.path.is_file():
            raise ValueError(
                "Expected a .tex file as entrypoint when using recursive parsing."
            )

        latex_text = self._load_file(self.path)
        latex_text = self._resolve_inputs(latex_text, self.root_path)
        latex_text = self._clean_latex_text(latex_text)
        return self._convert_to_markdown(latex_text)


class LatexChunker:
    """
    Splits a Markdown-formatted LaTeX document into semantically meaningful chunks.
    Suitable for embedding in vector databases like Weaviate.
    Args:
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters to overlap between chunks.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of characters to overlap between chunks.
        """
        self.headers_to_split_on = [
            ("#", "chapter"),
            ("##", "section"),
            ("###", "subsection"),
            ("####", "subsubsection"),
            ("#####", "paragraph"),
        ]
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=True,
        )
        self.char_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk(self, markdown_text: str) -> List[Document]:
        """
        Splits Markdown-formatted text into semantically meaningful and length-controlled chunks.

        Args:
            markdown_text: Markdown-formatted LaTeX content.

        Returns:
            List of LangChain Document objects.
        """
        docs = self.markdown_splitter.split_text(markdown_text)
        return self.char_splitter.split_documents(docs)
