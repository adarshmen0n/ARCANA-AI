"""Google Gemini Embedding Provider implementation with retry and fallback."""

import time
from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.errors import ProviderUnavailableException
from app.core.logging import get_logger
from app.embeddings.base import BaseEmbeddingProvider
from app.embeddings.mock_provider import MockEmbeddingProvider

logger = get_logger("app.embeddings.gemini")

GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
GEMINI_BATCH_URL = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents"


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Generates 768-dimensional dense embeddings using Google Gemini text-embedding-004."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._fallback = MockEmbeddingProvider(dimension=768)
        self._dim = 768

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        """Embeds a single text using Gemini API with automatic fallback."""
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("No valid Gemini API key configured. Using deterministic fallback provider.")
            return self._fallback.embed_text(text)

        payload = {
            "model": "models/text-embedding-004",
            "content": {"parts": [{"text": text[:8000]}]},
        }

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(
                        f"{GEMINI_EMBED_URL}?key={self.api_key}",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )

                if response.status_code == 200:
                    data = response.json()
                    return data["embedding"]["values"]

                if response.status_code in (429, 503):
                    time.sleep(0.5 * (2 ** (attempt - 1)))
                    continue

                logger.error(f"Gemini API returned error {response.status_code}: {response.text}")
                break

            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt}/{retries}): {str(e)}")
                if attempt < retries:
                    time.sleep(0.5 * (2 ** (attempt - 1)))

        logger.warning("Gemini API exhausted retries. Falling back to local deterministic embedding.")
        return self._fallback.embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a batch of texts."""
        return [self.embed_text(t) for t in texts]
