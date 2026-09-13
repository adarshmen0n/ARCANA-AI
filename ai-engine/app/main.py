"""ARCANA AI Engine — Main FastAPI Application.

Entrypoint for the AI Brain service. Provides health monitoring,
CORS security middleware, and modular API routers.
"""

from contextlib import asynccontextmanager
import logging
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from api import api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("arcana.brain")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for setup and teardown."""
    logger.info(
        "Initializing %s v%s (Environment: %s)",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ARCANA AI Brain — Educational Intelligence & Game Specification Engine",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_v1_router)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint verifying AI Engine status and version."""
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "version": settings.VERSION,
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Liveness health check endpoint."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
