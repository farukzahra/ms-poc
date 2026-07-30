from __future__ import annotations

import json

from semantic_kernel.functions import kernel_function

from app.models.chat import SourceItem
from app.rag.retriever import KnowledgeRetriever


class RagPlugin:
    """Semantic Kernel plugin for enterprise knowledge retrieval (RAG)."""

    def __init__(self, retriever: KnowledgeRetriever | None = None) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.sources: list[SourceItem] = []

    def reset(self) -> None:
        self.sources = []

    @kernel_function(
        name="search_knowledge",
        description="Search policy, contract, and product documentation (RAG)",
    )
    async def search_knowledge(self, query: str, customer_id: str = "") -> str:
        hits = await self.retriever.search(
            query,
            customer_id=customer_id or None,
        )
        self.sources.extend(SourceItem(**item) for item in hits)
        return json.dumps({"results": hits})
