"""Configuration and settings management for ARCANA AI Brain.

Adheres to 12-factor configuration principles using typed Pydantic models
and environment variables with sensible defaults.
"""

from functools import lru_cache
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env if present in project root
load_dotenv()


class Settings(BaseModel):
    # System & Environment
    PROJECT_NAME: str = "ARCANA AI Engine"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    HOST: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    LOG_LEVEL: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Security & CORS
    CORS_ORIGINS_RAW: str = Field(
        default_factory=lambda: os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8000",
        )
    )

    # AI / LLM Providers
    PRIMARY_LLM_PROVIDER: str = Field(default_factory=lambda: os.getenv("PRIMARY_LLM_PROVIDER", "mock"))
    FALLBACK_LLM_PROVIDER: str = Field(default_factory=lambda: os.getenv("FALLBACK_LLM_PROVIDER", "mock"))
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    OPENAI_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # Embeddings & Vector Store
    EMBEDDING_PROVIDER: str = Field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "sentence-transformers"))
    EMBEDDING_MODEL_NAME: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2"))
    VECTOR_STORE_PROVIDER: str = Field(default_factory=lambda: os.getenv("VECTOR_STORE_PROVIDER", "memory"))

    # Chunking
    CHUNKING_VERSION: str = Field(default_factory=lambda: os.getenv("CHUNKING_VERSION", "1.0"))
    MAX_CHUNK_SIZE: int = Field(default_factory=lambda: int(os.getenv("MAX_CHUNK_SIZE", "800")))
    CHUNK_OVERLAP: int = Field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "150")))

    # Policies
    LLM_TIMEOUT_SECONDS: int = Field(default_factory=lambda: int(os.getenv("LLM_TIMEOUT_SECONDS", "30")))
    LLM_MAX_RETRIES: int = Field(default_factory=lambda: int(os.getenv("LLM_MAX_RETRIES", "3")))

    @property
    def cors_origins(self) -> List[str]:
        """Return parsed list of allowed CORS origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton instance of application settings."""
    return Settings()
