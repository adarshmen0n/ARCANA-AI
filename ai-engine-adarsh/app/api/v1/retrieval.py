"""Semantic Retrieval API Endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel
from app.retrieval.models import RetrievalQuery, RetrievalResponse
from app.retrieval.service import retrieval_service

router = APIRouter(tags=["Retrieval"])


class IndexDocumentResponse(BaseModel):
    document_id: str
    chunks_indexed: int
    status: str = "indexed"


@router.post(
    "/documents/{document_id}/index",
    response_model=IndexDocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def index_document_vectors(document_id: str) -> IndexDocumentResponse:
    """Generates vector embeddings for all document chunks and adds them to the vector store."""
    indexed_count = retrieval_service.index_document(document_id)
    return IndexDocumentResponse(document_id=document_id, chunks_indexed=indexed_count)


@router.post(
    "/retrieval/query",
    response_model=RetrievalResponse,
    status_code=status.HTTP_200_OK,
)
async def query_knowledge_base(query_request: RetrievalQuery) -> RetrievalResponse:
    """Performs semantic vector search across indexed educational content."""
    return retrieval_service.query(query_request)
