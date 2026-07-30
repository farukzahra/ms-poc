"""Upload local data/*.md to Azure Blob Storage."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.storage.blob import upload_documents_to_blob  # noqa: E402


def main() -> None:
    count = upload_documents_to_blob()
    print(f"Uploaded {count} documents to Azure Blob")


if __name__ == "__main__":
    main()
