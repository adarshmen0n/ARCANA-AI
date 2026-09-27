"""Lesson Generator creating bite-sized educational lessons tailored to difficulty."""

import uuid
from typing import List, Optional
from app.knowledge.models import Concept
from app.generation.models import Lesson
from app.rag.service import rag_service
from app.providers.factory import get_llm_provider
from app.core.logging import get_logger

logger = get_logger("app.generation.lesson_generator")


class LessonGenerator:
    """Generates structured, pedagogical, engaging micro-lessons grounded in curriculum content."""

    def __init__(self):
        self.llm = get_llm_provider()

    def generate_lesson(
        self,
        concept: Concept,
        difficulty: int = 2,
        document_id: Optional[str] = None,
    ) -> Lesson:
        """Constructs a comprehensive micro-lesson with hook, core explanation, analogy, and takeaways."""
        logger.info(f"Generating lesson for concept '{concept.name}' at difficulty {difficulty}")

        # Retrieve grounding context if document_id is provided
        grounding_chunks = concept.source_chunk_ids
        context_text = concept.definition

        if document_id:
            try:
                from app.rag.models import RAGQueryRequest
                rag_resp = rag_service.answer_query(
                    RAGQueryRequest(
                        query=f"Explain {concept.name} and provide practical examples and edge cases.",
                        document_id=document_id,
                        max_context_chunks=2,
                    )
                )
                if rag_resp.answer:
                    context_text = rag_resp.answer
                    grounding_chunks = list(set(grounding_chunks + rag_resp.source_chunk_ids))
            except Exception as e:
                logger.warning(f"Could not retrieve additional RAG context: {e}")

        # Narrative hook tailored to difficulty
        hooks = {
            1: f"Welcome to the realm of {concept.topic}. Have you ever wondered how computers manage multiple demanding tasks seamlessly?",
            2: f"Imagine stepping into a high-concurrency operating system core. Today, you unlock the secrets of {concept.name}.",
            3: f"System bottlenecks threaten to stall the entire computing pipeline! Mastering {concept.name} is the key to restoring throughput.",
            4: f"Under extreme workloads, default scheduling mechanisms degrade. In this lesson, we dissect the architecture of {concept.name}.",
            5: f"Mission Critical: High-frequency kernel threads require optimal scheduling guarantees. Evaluate the limits of {concept.name}.",
        }
        hook = hooks.get(difficulty, hooks[2])

        # Educational analogy
        if "fcfs" in concept.concept_id or "first-come" in concept.name.lower():
            analogy = (
                "Think of a line at a grocery store checkout with a single cashier: "
                "the customer who arrived first is served first, regardless of whether they have one item or a full cart."
            )
        elif "round_robin" in concept.concept_id or "round robin" in concept.name.lower():
            analogy = (
                "Imagine a game of chess with a strict 30-second timer per turn. "
                "Each player gets a fixed time quantum before passing the turn, preventing any single player from monopolizing the board."
            )
        elif "priority" in concept.concept_id:
            analogy = (
                "Consider an emergency room triage: patients with life-threatening conditions are treated immediately, "
                "regardless of their arrival time relative to routine checkups."
            )
        else:
            analogy = (
                f"Think of {concept.name} as a specialized conductor directing a complex orchestra, "
                "ensuring each instrument performs at the right moment to maintain harmony."
            )

        # Key takeaways
        takeaways = [
            f"Definition: {concept.name} governs how the system allocates resources under the {concept.topic} paradigm.",
            f"Operational Mechanism: {concept.definition}",
            f"Trade-off: Balances computational overhead against system responsiveness and fairness.",
        ]

        # Common misconceptions
        misconceptions = concept.common_misconceptions or [
            f"Believing that {concept.name} is optimal in all operating environments without considering workload variance.",
            f"Overlooking context-switching overhead when configuring system parameters.",
        ]

        title = f"Mastering {concept.name}: Core Principles & Mechanics"

        return Lesson(
            concept_id=concept.concept_id,
            concept_name=concept.name,
            title=title,
            difficulty=difficulty,
            story_hook=hook,
            core_explanation=f"{concept.definition} {context_text}",
            analogy=analogy,
            key_takeaways=takeaways,
            common_misconceptions=misconceptions,
            source_chunks=grounding_chunks,
        )


lesson_generator = LessonGenerator()
