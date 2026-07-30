from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import settings


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    title: str
    source: str
    text: str
    customer_id: str | None = None


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def load_documents(data_dir: str | Path | None = None) -> list[DocumentChunk]:
    root = Path(data_dir or settings.data_dir)
    chunks: list[DocumentChunk] = []
    if not root.exists():
        return chunks

    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = path.stem.replace("-", " ").title()
        source = str(path.relative_to(root)).replace("\\", "/")
        customer_id = None
        if "acme" in path.name.lower():
            customer_id = "ACME-001"
        for index, piece in enumerate(
            _chunk_text(text, settings.chunk_size, settings.chunk_overlap)
        ):
            chunks.append(
                DocumentChunk(
                    id=f"{source}:{index}",
                    title=title,
                    source=source,
                    text=piece,
                    customer_id=customer_id,
                )
            )
    return chunks


def _score(query: str, chunk: DocumentChunk) -> float:
    query_terms = {term for term in re.findall(r"[a-z0-9]+", query.lower()) if len(term) > 2}
    text = chunk.text.lower()
    if not query_terms:
        return 0.0
    hits = sum(1 for term in query_terms if term in text)
    title_bonus = 1.0 if any(term in chunk.title.lower() for term in query_terms) else 0.0
    return hits + title_bonus


class LocalKnowledgeStore:
    def __init__(self, chunks: list[DocumentChunk] | None = None) -> None:
        self.chunks = chunks if chunks is not None else load_documents()

    def search(self, query: str, customer_id: str | None = None, top_k: int = 4) -> list[DocumentChunk]:
        ranked = []
        for chunk in self.chunks:
            if customer_id and chunk.customer_id and chunk.customer_id != customer_id:
                continue
            score = _score(query, chunk)
            if score > 0:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in ranked[:top_k]]


def chunks_to_sources(chunks: list[DocumentChunk]) -> list[dict[str, str]]:
    return [
        {
            "title": chunk.title,
            "source": chunk.source,
            "snippet": chunk.text[:240],
        }
        for chunk in chunks
    ]
