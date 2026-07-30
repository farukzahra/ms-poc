from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AzureSearchRetriever:
    def __init__(self) -> None:
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient

        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_api_key),
        )

    async def search(
        self,
        query: str,
        customer_id: str | None = None,
        top_k: int = 4,
    ) -> list[dict[str, str]]:
        filter_expr = None
        if customer_id:
            filter_expr = f"customerId eq '{customer_id}'"

        results = self.client.search(
            search_text=query,
            filter=filter_expr,
            top=top_k,
            select=["title", "source", "content", "customerId"],
        )
        items: list[dict[str, str]] = []
        for row in results:
            items.append(
                {
                    "title": row.get("title", "Document"),
                    "source": row.get("source", "unknown"),
                    "snippet": (row.get("content") or "")[:240],
                }
            )
        return items
