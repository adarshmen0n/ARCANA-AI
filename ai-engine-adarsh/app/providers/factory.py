"""LLM Provider Factory."""

from typing import Optional
from app.core.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import MockLLMProvider
from app.providers.gemini_provider import GeminiLLMProvider


def get_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    """Returns the configured LLM provider instance.

    Default resolves to settings.AI_PROVIDER (mock or gemini).
    """
    provider = (provider_type or settings.AI_PROVIDER).lower()

    if provider == "gemini":
        return GeminiLLMProvider()
    elif provider == "mock":
        return MockLLMProvider()
    else:
        return MockLLMProvider()
