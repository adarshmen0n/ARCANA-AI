"""Google Gemini Embedding Provider implementation using official google-genai SDK."""

import time
from typing import List, Optional

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from app.core.config import settings
from app.core.logging import get_logger
from app.embeddings.base import BaseEmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider

logger = get_logger("app.embeddings.gemini")


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Generates 768-dimensional dense embeddings using Google GenAI SDK."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._fallback = MockEmbeddingProvider(dimension=768)
        self._dim = 768

        self._client = None
        if GENAI_AVAILABLE and self.api_key and not self.api_key.startswith("your_"):
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized live GenAI Embedding Client (text-embedding-004)")
            except Exception as e:
                logger.warning(f"Could not initialize GenAI Embedding Client ({e}). Fallback active.")

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        """Embeds text using live GenAI embedding API with fallback."""
        if not self._client:
            return self._fallback.embed_text(text)

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                response = self._client.models.embed_content(
                    model="text-embedding-004",
                    contents=text[:8000],
                )
                if response and response.embeddings:
                    return response.embeddings[0].values
                break
            except Exception as e:
                logger.warning(f"GenAI embedding call failed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(0.5 * (2 ** (attempt - 1)))

        return self._fallback.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds batch of texts."""
        return [self.embed_text(t) for t in texts]
