import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    index: int


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[Chunk]:
    """Split text into overlapping chunks, preferring paragraph and sentence
    boundaries so chunks stay semantically coherent for retrieval."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[Chunk] = []
    current = ""

    def push_current():
        nonlocal current
        trimmed = current.strip()
        if trimmed:
            chunks.append(Chunk(text=trimmed, index=len(chunks)))

    for paragraph in paragraphs:
        if len(current) + 2 + len(paragraph) <= chunk_size:
            current = f"{current}\n\n{paragraph}" if current else paragraph
            continue

        if current:
            push_current()
            current = current[-overlap:] if overlap else ""

        if len(paragraph) > chunk_size:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            for sentence in sentences:
                if len(current) + 1 + len(sentence) > chunk_size:
                    push_current()
                    current = sentence
                else:
                    current = f"{current} {sentence}" if current else sentence
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph

    push_current()
    return chunks