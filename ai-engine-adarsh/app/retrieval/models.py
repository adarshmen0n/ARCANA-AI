"""Data models for Semantic Retrieval."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    query: str = Field(..., min_length=2, description="Natural language search query")
    document_id: Optional[str] = Field(None, description="Optional document ID to restrict search scope")
    top_k: int = Field(default=5, ge=1, le=20, description="Maximum candidate chunks to return")
    similarity_threshold: float = Field(
        default=0.25, ge=0.0, le=1.0, description="Minimum cosine similarity cutoff"
    )


class RetrievedChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    text: str = Field(..., description="Content of the retrieved chunk")
    heading: str = Field(..., description="Associated section/chapter heading")
    page_number: Optional[int] = Field(None, description="Page number of origin")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score (0.0 to 1.0)")


class RetrievalResponse(BaseModel):
    query: str
    document_id_filter: Optional[str] = None
    total_candidates_searched: int
    retrieved_count: int
    results: List[RetrievedChunk]
