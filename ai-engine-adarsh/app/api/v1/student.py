"""FastAPI endpoints for Student State, Mastery updates, and adaptive difficulty."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from shared.schemas.student_mastery import StudentProfile, MasteryUpdateResult
from app.student.service import student_service
from app.student.models import StudentInteractionRecord
from app.difficulty.engine import difficulty_engine
from app.core.logging import get_logger

logger = get_logger("app.api.v1.student")
router = APIRouter(prefix="/students", tags=["Student & Mastery"])


class CreateStudentRequest(BaseModel):
    student_id: str = Field(..., description="Unique student ID")
    display_name: str = Field(default="Learner", description="Display name")


class AdaptiveDifficultyResponse(BaseModel):
    student_id: str
    concept_id: str
    content_difficulty: int
    student_mastery: float
    recommended_difficulty: int
    difficulty_label: str


@router.post("", response_model=StudentProfile, summary="Register or initialize student profile")
async def create_student(req: CreateStudentRequest):
    return student_service.get_or_create_student(req.student_id, req.display_name)


@router.get("", response_model=List[StudentProfile], summary="List all student profiles")
async def list_students():
    return student_service.list_students()


@router.get("/{student_id}", response_model=StudentProfile, summary="Retrieve a student's profile and mastery map")
async def get_student(student_id: str):
    return student_service.get_student(student_id)


@router.post("/{student_id}/interaction", response_model=MasteryUpdateResult, summary="Record a student interaction and calculate mastery update")
async def record_interaction(student_id: str, interaction: StudentInteractionRecord):
    # Ensure student_id in path matches body or inject it
    interaction.student_id = student_id
    result = student_service.record_interaction(student_id, interaction)
    return result


@router.get(
    "/{student_id}/adaptive-difficulty/{concept_id}",
    response_model=AdaptiveDifficultyResponse,
    summary="Compute recommended adaptive difficulty for a student on a concept",
)
async def get_adaptive_difficulty(
    student_id: str,
    concept_id: str,
    content_difficulty: int = Query(default=2, ge=1, le=5),
):
    profile = student_service.get_or_create_student(student_id)
    mastery_record = profile.concept_mastery.get(concept_id)
    current_score = mastery_record.mastery_score if mastery_record else 0.0

    recommended = difficulty_engine.calculate_student_difficulty(
        content_difficulty=content_difficulty,
        student_mastery=current_score,
    )

    return AdaptiveDifficultyResponse(
        student_id=student_id,
        concept_id=concept_id,
        content_difficulty=content_difficulty,
        student_mastery=current_score,
        recommended_difficulty=recommended,
        difficulty_label=difficulty_engine.get_difficulty_label(recommended),
    )
