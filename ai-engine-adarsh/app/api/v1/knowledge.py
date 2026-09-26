"""Knowledge Engine API Endpoints."""

from typing import List
from fastapi import APIRouter, status
from app.knowledge.models import Concept, ConceptRelationship, KnowledgeExtractionResult
from app.knowledge.engine import knowledge_engine

router = APIRouter(tags=["Knowledge"])


@router.post(
    "/documents/{document_id}/knowledge",
    response_model=KnowledgeExtractionResult,
    status_code=status.HTTP_200_OK,
)
async def extract_document_knowledge(document_id: str) -> KnowledgeExtractionResult:
    """Extracts structured concepts and semantic relationships from document content."""
    return knowledge_engine.extract_knowledge(document_id)


@router.get(
    "/documents/{document_id}/concepts",
    response_model=List[Concept],
    status_code=status.HTTP_200_OK,
)
async def get_document_concepts(document_id: str) -> List[Concept]:
    """Retrieves all extracted concepts for a document."""
    return knowledge_engine.get_concepts(document_id)


@router.get(
    "/documents/{document_id}/relationships",
    response_model=List[ConceptRelationship],
    status_code=status.HTTP_200_OK,
)
async def get_document_relationships(document_id: str) -> List[ConceptRelationship]:
    """Retrieves all semantic concept relationships for a document."""
    return knowledge_engine.get_relationships(document_id)
