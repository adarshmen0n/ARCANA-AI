"""Application Configuration using Pydantic Settings.

Reads configuration from environment variables or .env file with type validation.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "ARCANA-AI Brain"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Current environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode flag")

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # AI Provider Settings
    AI_PROVIDER: str = Field(default="mock", description="AI Provider: mock, gemini, etc.")
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    FALLBACK_MODEL: str = "gemini-2.5-pro"

    # Observability
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True


settings = Settings()
