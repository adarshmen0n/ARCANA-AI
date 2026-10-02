"""AI Tutor Service providing adaptive Socratic guidance and cognitive unsticking."""

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
    cognitive_depth_level: str = "adaptive"
    source_chunk_ids: List[str] = Field(default_factory=list)


class AITutorService:
    """Provides conversational Socratic tutoring calibrated to individual learner mastery state."""

    def __init__(self):
        self.llm = get_llm_provider()

    def ask_tutor(self, req: TutorQueryRequest) -> TutorResponse:
        """Formulates Socratic pedagogical guidance for the student."""
        logger.info(f"AI Tutor processing query for student {req.student_id} on {req.concept_id}: '{req.query}'")

        # 1. Fetch concept details
        concept = knowledge_engine.get_concept_by_id(req.concept_id)
        concept_name = concept.name if concept else req.concept_id.replace("_", " ").title()
        concept_def = concept.definition if concept else "Core systems and architectural concept."

        # 2. Inspect learner mastery profile to calibrate cognitive scaffolding
        mastery_score = 0.0
        learner_level = 1
        try:
            profile = student_service.get_student(req.student_id)
            learner_level = profile.level
            if req.concept_id in profile.concept_mastery:
                mastery_score = profile.concept_mastery[req.concept_id].mastery_score
        except Exception:
            pass

        depth_tier = "advanced" if mastery_score >= 0.70 else ("scaffolded" if mastery_score < 0.40 else "balanced")

        # 3. RAG grounded context if document_id is provided
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

        # 4. Formulate Socratic reply
        reply_lines = [
            f"Greetings, initiate! Let us dissect {concept_name} together.",
            f"You asked: '{req.query}'.",
            f"Core Invariant: {concept_def}",
        ]
        if rag_answer:
            reply_lines.append(f"Grounded detail: {rag_answer[:220]}...")

        # 5. Domain-specific Socratic probes calibrated to depth tier
        cid_lower = req.concept_id.lower()
        if "fcfs" in cid_lower or "first" in cid_lower:
            guiding_q = (
                "If a CPU-bound process with a 500ms burst arrives ahead of five 2ms I/O bursts, "
                "how does that affect overall turnaround and CPU utilization?"
                if depth_tier == "advanced"
                else "If a long process arrives first, how does that impact all subsequent shorter processes waiting behind it?"
            )
            action = "Trace the waiting time of each process in the FIFO ready queue to observe the Convoy Effect."
        elif "round_robin" in cid_lower:
            guiding_q = (
                "At what point does the cost of storing and restoring PCB registers exceed the interactive gains of preemption?"
                if depth_tier == "advanced"
                else "What happens if each process only gets a tiny fraction of a second before the CPU switches to the next?"
            )
            action = "Compare context-switch overhead with effective CPU computation time across small vs large time slices."
        elif "shortest_job" in cid_lower or "sjf" in cid_lower:
            guiding_q = (
                "How does exponential smoothing with parameter alpha allow an OS to approximate future bursts?"
                if depth_tier == "advanced"
                else "Can an operating system predict the exact duration of a future user burst before it executes?"
            )
            action = "Analyze why theoretical optimality differs from practical implementation heuristics."
        elif "priority" in cid_lower:
            guiding_q = (
                "How does Priority Inversion occur when a low-priority thread holds a mutex needed by a high-priority thread?"
                if depth_tier == "advanced"
                else "If high-priority tasks keep arriving continuously, what prevents low-priority tasks from starving?"
            )
            action = "Examine how Aging and Priority Inheritance protocols resolve indefinite blocking."
        else:
            guiding_q = f"Which fundamental condition in {concept_name} directly controls resource allocation?"
            action = "Review the definition and test each choice against that governing rule."

        return TutorResponse(
            student_id=req.student_id,
            concept_id=req.concept_id,
            reply=" ".join(reply_lines),
            guiding_question=guiding_q,
            suggested_action=action,
            cognitive_depth_level=depth_tier,
            source_chunk_ids=source_chunks,
        )


ai_tutor_service = AITutorService()
