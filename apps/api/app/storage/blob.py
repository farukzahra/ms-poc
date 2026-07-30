from __future__ import annotations

import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def _blob_service():
    from azure.storage.blob import BlobServiceClient

    return BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)


def upload_documents_to_blob(data_dir: str | Path | None = None) -> int:
    """Upload local markdown files to Azure Blob (source of truth)."""
    if not settings.azure_blob_configured:
        raise RuntimeError("Azure Blob Storage is not configured")

    source = Path(data_dir or settings.data_dir)
    client = _blob_service()
    container = client.get_container_client(settings.azure_storage_container)
    if not container.exists():
        container.create_container()

    count = 0
    for path in sorted(source.rglob("*.md")):
        blob_name = path.relative_to(source).as_posix()
        with path.open("rb") as handle:
            container.upload_blob(name=blob_name, data=handle, overwrite=True)
        count += 1
    logger.info("Uploaded %s documents to Azure Blob container %s", count, settings.azure_storage_container)
    return count


def sync_documents_from_blob(local_dir: str | Path | None = None) -> int:
    """Download markdown documents from Azure Blob when configured."""
    if not settings.azure_blob_configured:
        logger.info("Azure Blob not configured; using local data directory")
        return 0

    target = Path(local_dir or settings.data_dir)
    target.mkdir(parents=True, exist_ok=True)

    client = _blob_service()
    container = client.get_container_client(settings.azure_storage_container)
    count = 0
    for blob in container.list_blobs():
        if not blob.name.endswith(".md"):
            continue
        downloader = container.download_blob(blob.name)
        dest = target / Path(blob.name).name
        dest.write_bytes(downloader.readall())
        count += 1
    logger.info("Synced %s documents from Azure Blob", count)
    return count


def sync_and_ingest() -> tuple[int, int]:
    """Blob → local mirror → Azure AI Search index."""
    synced = sync_documents_from_blob()
    ingested = 0
    if settings.azure_search_configured and settings.azure_openai_configured:
        from app.rag.ingest import ingest_to_azure

        ingested = ingest_to_azure()
    return synced, ingested
