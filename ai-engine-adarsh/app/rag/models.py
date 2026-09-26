"""Data models for RAG Question Answering and Context Grounding."""

from typing import List, Optional
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Student question or conceptual query")
    document_id: Optional[str] = Field(None, description="Optional document ID to restrict knowledge domain")
    max_context_chunks: int = Field(default=4, ge=1, le=10, description="Maximum chunks to inject into context")
    similarity_threshold: float = Field(default=0.25, ge=0.0, le=1.0, description="Similarity threshold for retrieval")
    max_token_budget: int = Field(default=2000, ge=200, le=8000, description="Context token ceiling")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="Sampling temperature")


class SourceCitation(BaseModel):
    chunk_id: str = Field(..., description="ID of cited source chunk")
    heading: str = Field(..., description="Section or chapter heading of cited chunk")
    page_number: Optional[int] = Field(None, description="Source page number")
    similarity_score: float = Field(..., description="Cosine similarity score")
    snippet: str = Field(..., description="Short snippet from source content")


class RAGAnswer(BaseModel):
    query: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Grounded natural language educational answer")
    citations: List[SourceCitation] = Field(default_factory=list, description="Explicit source citations")
    source_chunk_ids: List[str] = Field(default_factory=list, description="All chunk IDs utilized in context")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Retrieval confidence score")
    grounded: bool = Field(default=True, description="Flag indicating if answer is grounded in retrieved chunks")
    model_used: str = Field(..., description="LLM provider and model name")
    latency_ms: float = Field(..., description="Total pipeline latency in milliseconds")
