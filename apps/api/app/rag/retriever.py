from __future__ import annotations

import logging
from pathlib import Path

from app.config import settings
from app.rag.local_store import DocumentChunk, LocalKnowledgeStore, chunks_to_sources, load_documents

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    def __init__(self) -> None:
        self._local = LocalKnowledgeStore()
        self._azure = None
        if settings.azure_search_configured:
            from app.rag.azure_search import AzureSearchRetriever

            self._azure = AzureSearchRetriever()

    async def search(
        self,
        query: str,
        customer_id: str | None = None,
        top_k: int = 4,
    ) -> list[dict[str, str]]:
        if self._azure:
            try:
                results = await self._azure.search(query, customer_id=customer_id, top_k=top_k)
                if results:
                    return results
            except Exception as exc:  # noqa: BLE001
                logger.warning("Azure Search failed, falling back to local RAG: %s", exc)

        chunks = self._local.search(query, customer_id=customer_id, top_k=top_k)
        return chunks_to_sources(chunks)


def ingest_local(data_dir: str | Path | None = None) -> int:
    chunks = load_documents(data_dir)
    logger.info("Loaded %s local document chunks", len(chunks))
    return len(chunks)
