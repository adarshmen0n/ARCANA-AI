"""FastAPI endpoints for GameSpecification generation consumed by the Game Engine."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from shared.schemas.game_specification import GameSpecification
from app.generation.models import NPCPersona
from app.generation.mission_generator import mission_generator
from app.knowledge.engine import knowledge_engine
from app.knowledge.models import Concept

router = APIRouter(prefix="/game-spec", tags=["Game Specification"])


class GenerateGameSpecRequest(BaseModel):
    concept_id: str = Field(..., description="Target educational concept key")
    difficulty: int = Field(default=2, ge=1, le=5, description="Challenge difficulty (1-5)")
    is_boss: bool = Field(default=False, description="Whether to generate a boss battle mission")
    persona: NPCPersona = Field(default=NPCPersona.ARCHMAGE_ALAN, description="NPC Persona for mission dialogue")
    document_id: Optional[str] = Field(None, description="Optional document ID for grounding context")


@router.post("/generate", response_model=GameSpecification, summary="Generate a validated GameSpecification for the Game Engine")
async def generate_game_specification(req: GenerateGameSpecRequest):
    concept = knowledge_engine.get_concept_by_id(req.concept_id)
    if not concept:
        concept = Concept(
            concept_id=req.concept_id,
            name=req.concept_id.replace("_", " ").title(),
            topic="Computer Science",
            definition=f"Core operating principles and mechanisms of {req.concept_id.replace('_', ' ').title()}.",
            difficulty=req.difficulty,
        )

    return mission_generator.generate_mission(
        concept=concept,
        difficulty=req.difficulty,
        is_boss=req.is_boss,
        persona=req.persona,
        document_id=req.document_id,
    )
