"""Main FastAPI Application Entrypoint for ARCANA-AI Brain.

Initializes middleware, routing, exception handlers, and observability.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.errors import (
    ArcanaException,
    arcana_exception_handler,
    generic_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle management."""
    setup_logging()
    logger = get_logger("app.main")
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Educational Intelligence Engine for Personalized Gamified Learning",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# -------------------------------------------------------------
# Middleware: Request ID and Latency Observability
# -------------------------------------------------------------
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)

    return response


# -------------------------------------------------------------
# Middleware: CORS Configuration
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Exception Handlers
# -------------------------------------------------------------
app.add_exception_handler(ArcanaException, arcana_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# -------------------------------------------------------------
# Routers
# -------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root Convenience Endpoints
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["Root"])
async def root_health():
    """Convenience alias for /api/v1/health."""
    from app.api.v1.health import get_health
    return await get_health()


@app.get("/health/ready", tags=["Root"])
async def root_ready():
    """Convenience alias for /api/v1/health/ready."""
    from app.api.v1.health import get_readiness
    return await get_readiness()
