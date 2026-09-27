"""FastAPI endpoints for generating Lessons, Questions, Hints, and Boss Encounters."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.generation.models import Lesson, GeneratedQuestion, BossEncounter
from app.generation.lesson_generator import lesson_generator
from app.generation.question_generator import question_generator
from app.generation.boss_generator import boss_generator
from app.knowledge.engine import knowledge_engine
from app.knowledge.models import Concept

router = APIRouter(prefix="/generation", tags=["Content Generation"])


class GenerateLessonRequest(BaseModel):
    concept_id: str
    difficulty: int = Field(default=2, ge=1, le=5)
    document_id: Optional[str] = None


class GenerateQuestionRequest(BaseModel):
    concept_id: str
    difficulty: int = Field(default=2, ge=1, le=5)
    challenge_type: str = Field(default="mcq")


class GenerateBossRequest(BaseModel):
    concept_id: str
    phases: int = Field(default=2, ge=1, le=5)


def _resolve_concept(concept_id: str) -> Concept:
    concept = knowledge_engine.get_concept_by_id(concept_id)
    if not concept:
        concept = Concept(
            concept_id=concept_id,
            name=concept_id.replace("_", " ").title(),
            topic="Computer Science",
            definition=f"Core operating principles and mechanisms of {concept_id.replace('_', ' ').title()}.",
            difficulty=2,
        )
    return concept


@router.post("/lesson", response_model=Lesson, summary="Generate an engaging micro-lesson for a concept")
async def generate_lesson(req: GenerateLessonRequest):
    concept = _resolve_concept(req.concept_id)
    return lesson_generator.generate_lesson(
        concept=concept,
        difficulty=req.difficulty,
        document_id=req.document_id,
    )


@router.post("/question", response_model=GeneratedQuestion, summary="Generate an assessment challenge with progressive hints")
async def generate_question(req: GenerateQuestionRequest):
    concept = _resolve_concept(req.concept_id)
    return question_generator.generate_question(
        concept=concept,
        difficulty=req.difficulty,
        challenge_type=req.challenge_type,
    )


@router.post("/boss", response_model=BossEncounter, summary="Generate a multi-phase boss battle for a concept milestone")
async def generate_boss(req: GenerateBossRequest):
    concept = _resolve_concept(req.concept_id)
    return boss_generator.generate_full_encounter(
        concept=concept,
        phases=req.phases,
    )
