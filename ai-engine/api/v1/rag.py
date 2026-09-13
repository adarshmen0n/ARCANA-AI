"""RAG and semantic retrieval endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from rag.engine import RAGEngine, GroundedAnswer
from services.deps import get_rag_engine

router = APIRouter(prefix="/rag", tags=["RAG & Retrieval"])


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 4
    chapter: Optional[str] = None
    document_id: Optional[str] = None


@router.post("/query", response_model=GroundedAnswer)
async def query_rag(
    req: RAGQueryRequest,
    rag_engine: RAGEngine = Depends(get_rag_engine),
):
    """Retrieve grounded answers and source chunk citations from ingested educational material."""
    return rag_engine.query(
        query_text=req.query,
        top_k=req.top_k,
        chapter=req.chapter,
        document_id=req.document_id,
    )
