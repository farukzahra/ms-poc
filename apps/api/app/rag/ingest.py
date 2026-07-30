"""Ingest markdown documents into Azure AI Search when configured."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from app.config import settings
from app.rag.embeddings import embed_text
from app.rag.local_store import load_documents

logger = logging.getLogger(__name__)


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
        vector = embed_text(chunk.text) or None
        documents.append(
            {
                "id": doc_id,
                "title": chunk.title,
                "source": chunk.source,
                "content": chunk.text,
                "customerId": chunk.customer_id or "",
                "contentVector": vector,
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
