"""Learning Graph API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.learning_graph.models import LearningPath, NextConceptRecommendation
from app.learning_graph.service import learning_graph_service

router = APIRouter(tags=["Learning Graph"])


class NextConceptRequest(BaseModel):
    completed_concept_ids: List[str] = Field(default_factory=list, description="IDs of concepts already mastered")
    weak_concept_id: Optional[str] = Field(None, description="Optional struggling concept to trigger remediation")


@router.get(
    "/documents/{document_id}/graph",
    response_model=LearningPath,
    status_code=status.HTTP_200_OK,
)
async def get_learning_graph(document_id: str) -> LearningPath:
    """Retrieves the full topological Learning Graph path for a document."""
    return learning_graph_service.get_learning_path(document_id)


@router.post(
    "/documents/{document_id}/next-concept",
    response_model=NextConceptRecommendation,
    status_code=status.HTTP_200_OK,
)
async def recommend_next_concept(
    document_id: str,
    request: NextConceptRequest,
) -> NextConceptRecommendation:
    """Selects the next optimal concept to learn based on student progress and prerequisite readiness."""
    return learning_graph_service.recommend_next_concept(
        document_id=document_id,
        completed_concept_ids=request.completed_concept_ids,
        weak_concept_id=request.weak_concept_id,
    )
