"""AI Tutor Service providing Socratic guidance and conversational unsticking."""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.student.service import student_service
from app.knowledge.engine import knowledge_engine
from app.rag.service import rag_service
from app.providers.factory import get_llm_provider
from app.core.logging import get_logger

logger = get_logger("app.tutor.service")


class TutorQueryRequest(BaseModel):
    student_id: str
    concept_id: str
    query: str
    document_id: Optional[str] = None


class TutorResponse(BaseModel):
    student_id: str
    concept_id: str
    reply: str
    guiding_question: str
    suggested_action: str
    source_chunk_ids: List[str] = Field(default_factory=list)


class AITutorService:
    """Provides conversational Socratic tutoring to unstick learners without spoiling answers."""

    def __init__(self):
        self.llm = get_llm_provider()

    def ask_tutor(self, req: TutorQueryRequest) -> TutorResponse:
        """Formulates Socratic pedagogical guidance for the student."""
        logger.info(f"AI Tutor processing query for student {req.student_id} on {req.concept_id}: '{req.query}'")

        # Fetch concept details
        concept = knowledge_engine.get_concept_by_id(req.concept_id)
        concept_name = concept.name if concept else req.concept_id.replace("_", " ").title()
        concept_def = concept.definition if concept else "Core systems and architectural concept."

        # RAG grounded context if document_id is provided
        rag_answer = ""
        source_chunks: List[str] = []
        if req.document_id:
            try:
                from app.rag.models import RAGQueryRequest
                rag_res = rag_service.answer_query(
                    RAGQueryRequest(
                        query=f"Explain {concept_name} for a student asking: {req.query}",
                        document_id=req.document_id,
                        max_context_chunks=2,
                    )
                )
                rag_answer = rag_res.answer
                source_chunks = rag_res.source_chunk_ids
            except Exception as e:
                logger.warning(f"RAG retrieval skipped for tutor: {e}")

        # Socratic reply construction
        reply_lines = [
            f"Greetings, traveler! Let us examine {concept_name} together.",
            f"You asked: '{req.query}'.",
            f"Here is a key principle to keep in mind: {concept_def}",
        ]
        if rag_answer:
            reply_lines.append(f"Grounded detail: {rag_answer[:200]}...")

        # Guiding Socratic question tailored to domain
        if "fcfs" in req.concept_id.lower() or "first" in req.concept_id.lower():
            guiding_q = "If a long process arrives first, how does that impact all subsequent shorter processes waiting behind it?"
            action = "Trace the waiting time of the second and third processes in the queue."
        elif "round_robin" in req.concept_id.lower():
            guiding_q = "What happens if each process only gets a tiny fraction of a second before the CPU switches to the next?"
            action = "Compare context-switch overhead with effective CPU computation time."
        elif "priority" in req.concept_id.lower():
            guiding_q = "If high-priority tasks keep arriving continuously, what happens to the low-priority tasks at the back?"
            action = "Consider how the Aging technique prevents indefinite starvation."
        else:
            guiding_q = f"Which fundamental condition in {concept_name} directly controls resource allocation?"
            action = "Review the definition and test each choice against that rule."

        return TutorResponse(
            student_id=req.student_id,
            concept_id=req.concept_id,
            reply=" ".join(reply_lines),
            guiding_question=guiding_q,
            suggested_action=action,
            source_chunk_ids=source_chunks,
        )


ai_tutor_service = AITutorService()
