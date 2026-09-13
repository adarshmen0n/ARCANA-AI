"""AI Tutor conversational endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from schemas.personalization import StudentState
from services.tutor import AITutorService, TutorResponse
from services.deps import get_tutor_service

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])


class TutorRequest(BaseModel):
    question: str
    student_state: Optional[StudentState] = None
    subject: Optional[str] = None


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(
    req: TutorRequest,
    tutor: AITutorService = Depends(get_tutor_service),
):
    """Interact with the personalized AI Tutor, grounded in source documents and tailored to student level."""
    return tutor.ask_tutor(
        question=req.question,
        student_state=req.student_state,
        subject=req.subject,
    )
