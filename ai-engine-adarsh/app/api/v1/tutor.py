"""FastAPI endpoint for AI Socratic Tutor."""

from fastapi import APIRouter
from app.tutor.service import ai_tutor_service, TutorQueryRequest, TutorResponse

router = APIRouter(prefix="/tutor", tags=["AI Socratic Tutor"])


@router.post("/ask", response_model=TutorResponse, summary="Ask the AI Tutor for Socratic hints and conceptual unsticking")
async def ask_tutor(req: TutorQueryRequest):
    return ai_tutor_service.ask_tutor(req)
