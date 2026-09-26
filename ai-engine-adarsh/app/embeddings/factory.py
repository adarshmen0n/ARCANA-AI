"""Embedding Provider Factory."""

from typing import Optional
from app.core.config import settings
from app.embeddings.base import BaseEmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.embeddings.gemini_provider import GeminiEmbeddingProvider


def get_embedding_provider(provider_type: Optional[str] = None) -> BaseEmbeddingProvider:
    """Returns the configured embedding provider instance.

    Default resolves to settings.AI_PROVIDER (mock or gemini).
    """
    provider = (provider_type or settings.AI_PROVIDER).lower()

    if provider == "gemini":
        return GeminiEmbeddingProvider()
    elif provider == "mock":
        return MockEmbeddingProvider(dimension=256)
    else:
        # Default fallback
        return MockEmbeddingProvider(dimension=256)
