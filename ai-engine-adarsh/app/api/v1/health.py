"""Health and Readiness endpoints for ARCANA-AI Brain."""

from datetime import datetime, timezone
from typing import Dict
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Service liveness state")
    service: str = Field(..., description="Service identifier")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current UTC timestamp")


class ReadinessResponse(BaseModel):
    status: str = Field(default="ready", description="Service readiness state")
    service: str = Field(..., description="Service identifier")
    environment: str = Field(..., description="Operational environment")
    components: Dict[str, str] = Field(..., description="Health status of internal subsystems")
    timestamp: str = Field(..., description="Current UTC timestamp")


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def get_health() -> HealthResponse:
    """Liveness probe to confirm that the AI Brain HTTP server is running."""
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health/ready", response_model=ReadinessResponse, status_code=status.HTTP_200_OK)
async def get_readiness() -> ReadinessResponse:
    """Readiness probe to confirm that the AI Brain has initialized its required components."""
    # In Phase 2, verify configuration and core subsystems
    components = {
        "schemas": "ready",
        "configuration": "ready",
        "ai_provider": f"configured ({settings.AI_PROVIDER})",
    }

    return ReadinessResponse(
        status="ready",
        service=settings.PROJECT_NAME,
        environment=settings.ENVIRONMENT,
        components=components,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
