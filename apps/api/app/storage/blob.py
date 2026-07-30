from __future__ import annotations

import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def sync_documents_from_blob(local_dir: str | Path | None = None) -> int:
    """Download markdown documents from Azure Blob when configured."""
    if not settings.azure_blob_configured:
        logger.info("Azure Blob not configured; using local data directory")
        return 0

    from azure.storage.blob import BlobServiceClient

    target = Path(local_dir or settings.data_dir)
    target.mkdir(parents=True, exist_ok=True)

    client = BlobServiceClient.from_connection_string(
        settings.azure_storage_connection_string
    )
    container = client.get_container_client("documents")
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
