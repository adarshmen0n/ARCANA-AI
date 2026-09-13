"""FastAPI dependencies and shared service singletons for ARCANA AI Brain."""

from functools import lru_cache
from orchestration.pipeline import ArcanaBrainPipeline
from providers.router import ProviderRouter
from rag.engine import RAGEngine
from services.tutor import AITutorService
from config.settings import get_settings


@lru_cache()
def get_pipeline() -> ArcanaBrainPipeline:
    """Singleton pipeline instance shared across API requests."""
    router = ProviderRouter()
    return ArcanaBrainPipeline(provider_router=router)


def get_rag_engine() -> RAGEngine:
    """Access the RAG subsystem backed by the shared pipeline vector store."""
    pipe = get_pipeline()
    return RAGEngine(
        vector_store=pipe.vector_store,
        embedding_engine=pipe.embedding_engine,
        provider_router=pipe.router,
    )


def get_tutor_service() -> AITutorService:
    """Access the AI Tutor service backed by RAG and the provider router."""
    pipe = get_pipeline()
    rag = get_rag_engine()
    return AITutorService(rag_engine=rag, provider_router=pipe.router)
