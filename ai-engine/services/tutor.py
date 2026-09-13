"""AI Tutor service providing grounded, personalized educational assistance."""

import logging
from typing import Optional
from schemas.base import ArcanaBaseModel
from schemas.personalization import StudentState
from rag.engine import RAGEngine
from providers.router import ProviderRouter

logger = logging.getLogger("arcana.services.tutor")


class TutorResponse(ArcanaBaseModel):
    """Personalized response from the AI Tutor."""

    answer: str
    adapted_for_level: int
    source_references: list[str]
    suggested_followup: str


class AITutorService:
    """Provides personalized tutoring grounded in source material and tailored to learner level."""

    def __init__(self, rag_engine: RAGEngine, provider_router: ProviderRouter):
        self.rag_engine = rag_engine
        self.provider_router = provider_router

    def ask_tutor(
        self,
        question: str,
        student_state: Optional[StudentState] = None,
        subject: Optional[str] = None,
    ) -> TutorResponse:
        level = student_state.current_level if student_state else 1

        # Retrieve source grounding
        grounded = self.rag_engine.query(query_text=question, top_k=3)

        # Style based on student level
        simplicity = (
            "Explain intuitively using simple analogies and beginner-friendly language."
            if level <= 2
            else "Provide a technical, precise explanation covering edge cases and architecture."
        )

        system_prompt = (
            "You are ARCANA, an empathetic and mathematically rigorous AI Tutor. "
            f"The student is currently at Level {level}. {simplicity} "
            "Use the provided source context for facts. Do not invent details not grounded in the source."
        )

        user_prompt = (
            f"Source Material:\n{grounded.answer}\n\n"
            f"Student Question: {question}\n\n"
            "Provide an encouraging, clear explanation followed by a suggested next practice topic."
        )

        tutor_text = self.provider_router.generate(user_prompt, system_prompt=system_prompt)

        return TutorResponse(
            answer=tutor_text.strip(),
            adapted_for_level=level,
            source_references=grounded.source_chunk_ids,
            suggested_followup="Would you like to practice a scenario mission on this concept?",
        )
