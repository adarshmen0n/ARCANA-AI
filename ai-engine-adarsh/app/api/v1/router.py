"""API v1 Central Router for ARCANA-AI Brain."""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chunks import router as chunks_router
from app.api.v1.retrieval import router as retrieval_router
from app.api.v1.rag import router as rag_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.graph import router as graph_router
from app.api.v1.student import router as student_router
from app.api.v1.objectives import router as objectives_router
from app.api.v1.generation import router as generation_router
from app.api.v1.game_spec import router as game_spec_router
from app.api.v1.telemetry import router as telemetry_router
from app.api.v1.sequencer import router as sequencer_router
from app.api.v1.tutor import router as tutor_router

api_router = APIRouter()

# Register endpoint groups
api_router.include_router(health_router)
api_router.include_router(documents_router)
api_router.include_router(chunks_router)
api_router.include_router(retrieval_router)
api_router.include_router(rag_router)
api_router.include_router(knowledge_router)
api_router.include_router(graph_router)
api_router.include_router(student_router)
api_router.include_router(objectives_router)
api_router.include_router(generation_router)
api_router.include_router(game_spec_router)
api_router.include_router(telemetry_router)
api_router.include_router(sequencer_router)
api_router.include_router(tutor_router)
