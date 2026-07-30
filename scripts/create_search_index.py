"""Create Azure AI Search index for ms-poc RAG."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.config import settings  # noqa: E402


def main() -> None:
    if not settings.azure_search_configured:
        raise SystemExit("Azure Search not configured in .env")

    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        HnswAlgorithmConfiguration,
        SearchField,
        SearchFieldDataType,
        SearchIndex,
        SimpleField,
        VectorSearch,
        VectorSearchProfile,
    )

    client = SearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_api_key),
    )

    index = SearchIndex(
        name=settings.azure_search_index,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="title", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            SimpleField(name="customerId", type=SearchFieldDataType.String, filterable=True),
            SearchField(
                name="contentVector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="default",
            ),
        ],
        vector_search=VectorSearch(
            profiles=[VectorSearchProfile(name="default", algorithm_configuration_name="default")],
            algorithms=[HnswAlgorithmConfiguration(name="default")],
        ),
    )

    client.create_or_update_index(index)
    print(f"Index '{settings.azure_search_index}' ready")


if __name__ == "__main__":
    os.chdir(ROOT / "apps" / "api")
    main()
