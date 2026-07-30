"""Ingest markdown documents into Azure AI Search when configured."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from app.config import settings
from app.rag.local_store import load_documents

logger = logging.getLogger(__name__)


def _embedding(text: str) -> list[float]:
    if not settings.azure_openai_configured or not settings.azure_embedding_deployment:
        return []

    from openai import AzureOpenAI

    client = AzureOpenAI(
        azure_endpoint=settings.azure_ai_endpoint,
        api_key=settings.azure_ai_api_key,
        api_version="2024-10-21",
    )
    response = client.embeddings.create(
        model=settings.azure_embedding_deployment,
        input=text,
    )
    return response.data[0].embedding


def ingest_to_azure(data_dir: str | Path | None = None) -> int:
    if not settings.azure_search_configured:
        raise RuntimeError("Azure AI Search is not configured")

    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient

    client = SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_api_key),
    )

    chunks = load_documents(data_dir)
    documents = []
    for chunk in chunks:
        doc_id = hashlib.sha256(chunk.id.encode()).hexdigest()[:32]
        documents.append(
            {
                "id": doc_id,
                "title": chunk.title,
                "source": chunk.source,
                "content": chunk.text,
                "customerId": chunk.customer_id or "",
                "contentVector": _embedding(chunk.text) or None,
            }
        )

    if not documents:
        return 0

    client.upload_documents(documents=documents)
    logger.info("Uploaded %s documents to Azure AI Search", len(documents))
    return len(documents)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if settings.azure_search_configured and settings.azure_openai_configured:
        count = ingest_to_azure()
        print(f"Ingested {count} chunks to Azure AI Search")
    else:
        from app.rag.retriever import ingest_local

        count = ingest_local()
        print(f"Loaded {count} local chunks (Azure not configured)")


if __name__ == "__main__":
    main()
