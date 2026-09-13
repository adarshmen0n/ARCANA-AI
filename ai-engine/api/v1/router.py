"""Aggregates all API v1 routers for ARCANA AI Brain."""

from fastapi import APIRouter
from .documents import router as documents_router
from .jobs import router as jobs_router
from .rag import router as rag_router
from .tutor import router as tutor_router
from .analytics import router as analytics_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(documents_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(tutor_router)
api_v1_router.include_router(analytics_router)
