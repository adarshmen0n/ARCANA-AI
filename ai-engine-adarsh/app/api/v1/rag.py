"""RAG API Endpoints."""

from fastapi import APIRouter, status
from app.rag.models import RAGAnswer, RAGQueryRequest
from app.rag.service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/answer", response_model=RAGAnswer, status_code=status.HTTP_200_OK)
async def generate_grounded_answer(request: RAGQueryRequest) -> RAGAnswer:
    """Answers student questions using retrieved, grounded study material with source citations."""
    return rag_service.answer_query(request)
