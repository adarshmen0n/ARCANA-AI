"""FastAPI endpoints for Bloom's Taxonomy Learning Objectives."""

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.objectives.generator import objective_generator
from app.objectives.models import ConceptObjectivesResult, LearningObjective
from app.knowledge.models import Concept
from app.knowledge.engine import knowledge_engine

router = APIRouter(prefix="/objectives", tags=["Learning Objectives"])


class GenerateObjectivesRequest(BaseModel):
    concept_id: str = Field(..., description="Target concept ID")
    concept_name: Optional[str] = Field(None, description="Concept display name")
    difficulties: Optional[List[int]] = Field(
        default=[1, 2, 3, 4, 5],
        description="Target difficulty levels (1-5)",
    )


@router.post("/generate", response_model=ConceptObjectivesResult, summary="Generate Bloom's taxonomy objectives for a concept")
async def generate_objectives(req: GenerateObjectivesRequest):
    # Lookup concept from knowledge engine if available, or create minimal instance
    concept = None
    for c in knowledge_engine.list_all_concepts():
        if c.concept_id == req.concept_id:
            concept = c
            break

    if not concept:
        concept = Concept(
            concept_id=req.concept_id,
            name=req.concept_name or req.concept_id.replace("_", " ").title(),
            topic="General",
            definition=f"Core principles and mechanisms of {req.concept_name or req.concept_id}.",
            difficulty=2,
        )

    return objective_generator.generate_objectives_for_concept(
        concept=concept,
        difficulties=req.difficulties,
    )
