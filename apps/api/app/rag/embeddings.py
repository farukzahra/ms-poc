from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


def embed_text(text: str) -> list[float]:
    if not settings.azure_openai_configured or not settings.azure_embedding_deployment:
        return []

    from openai import AzureOpenAI

    client = AzureOpenAI(
        azure_endpoint=settings.azure_ai_endpoint,
        api_key=settings.azure_ai_api_key,
        api_version=settings.azure_openai_api_version,
    )
    response = client.embeddings.create(
        model=settings.azure_embedding_deployment,
        input=text,
    )
    return response.data[0].embedding
