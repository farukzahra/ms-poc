from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from semantic_kernel.functions import kernel_function

from app.models.chat import SourceItem
from app.rag.retriever import KnowledgeRetriever


def _preview_hits(hits: list[dict[str, str]], limit: int = 280) -> str:
    text = json.dumps({"results": hits}, default=str)
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 1]}…"


@dataclass
class PluginCallRecord:
    tool: str
    arguments: dict[str, str] = field(default_factory=dict)
    result_preview: str = ""
    duration_ms: float | None = None


class RagPlugin:
    """Semantic Kernel plugin for enterprise knowledge retrieval (RAG)."""

    def __init__(self, retriever: KnowledgeRetriever | None = None) -> None:
        self.retriever = retriever or KnowledgeRetriever()
        self.sources: list[SourceItem] = []
        self.call_records: list[PluginCallRecord] = []

    def reset(self) -> None:
        self.sources = []
        self.call_records = []

    @kernel_function(
        name="search_knowledge",
        description="Search policy, contract, and product documentation (RAG)",
    )
    async def search_knowledge(self, query: str, customer_id: str = "") -> str:
        args = {"query": query}
        if customer_id:
            args["customer_id"] = customer_id

        started = time.perf_counter()
        hits = await self.retriever.search(
            query,
            customer_id=customer_id or None,
        )
        duration_ms = round((time.perf_counter() - started) * 1000, 1)
        self.sources.extend(SourceItem(**item) for item in hits)
        self.call_records.append(
            PluginCallRecord(
                tool="search_knowledge",
                arguments=args,
                result_preview=_preview_hits(hits),
                duration_ms=duration_ms,
            )
        )
        return json.dumps({"results": hits})
