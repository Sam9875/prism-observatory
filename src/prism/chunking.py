from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from prism.types import SourceDoc


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in text.split("\n\n") if part.strip()]


def split_docs(docs: list[SourceDoc]) -> list[Document]:
    """Pack whole paragraphs, and use LangChain's splitter only inside a long one.

    Overlap keeps the previous paragraph when a chunk rolls over, so a fact on
    the boundary stays citable without slicing a word in half.
    """
    long_splitter = RecursiveCharacterTextSplitter(
        chunk_size=650,
        chunk_overlap=0,
        separators=["\n", ". ", " "],
    )
    documents: list[Document] = []
    for doc in docs:
        pieces: list[str] = []
        buffer: list[str] = []
        size = 0
        for paragraph in _paragraphs(doc.text):
            parts = [paragraph] if len(paragraph) <= 650 else long_splitter.split_text(paragraph)
            for part in parts:
                if buffer and size + len(part) > 700:
                    pieces.append("\n\n".join(buffer))
                    buffer = buffer[-1:]
                    size = len(buffer[0])
                buffer.append(part)
                size += len(part)
        if buffer:
            pieces.append("\n\n".join(buffer))
        for index, piece in enumerate(pieces or [doc.text]):
            documents.append(
                Document(
                    page_content=f"{doc.title}. {piece}",
                    metadata={
                        "chunk_id": f"{doc.id}-{index}",
                        "doc_id": doc.id,
                        "title": doc.title,
                        "archive": doc.archive,
                        "entities": list(doc.entities),
                        "index": index,
                        "passage": piece,
                    },
                )
            )
    return documents
