"""Lesson Generator producing grounded instructional content."""

from typing import List, Optional
from schemas.knowledge import Concept
from schemas.generation import Lesson, LearningObjective
from schemas.document import Chunk
from schemas.base import generate_id
from .base import BaseGenerator


class LessonGenerator(BaseGenerator):
    """Generates concise, pedagogically clear lessons grounded in source material."""

    def generate_lesson(
        self,
        concept: Concept,
        objective: LearningObjective,
        source_chunks: Optional[List[Chunk]] = None,
    ) -> Lesson:
        ref_ids = [c.chunk_id for c in source_chunks] if source_chunks else concept.source_chunk_ids

        # Grounding text from source chunks if present
        source_snippet = ""
        if source_chunks:
            source_snippet = " ".join(c.text[:200] for c in source_chunks[:2])

        explanation = (
            f"{concept.description} In the context of {concept.name}, understanding this concept "
            f"allows learners to master core computational principles."
        )
        if source_snippet:
            explanation = f"{explanation} {source_snippet}"

        examples = [
            f"Basic example demonstrating {concept.name} syntax and semantics.",
            f"Real-world application where {concept.name} manages state efficiently.",
        ]

        key_points = [
            f"{concept.name} forms a core prerequisite for higher-level operations.",
            f"Always check edge cases when configuring {concept.name}.",
            "Mastery requires consistent hands-on verification.",
        ]

        analogy = f"Think of {concept.name} like an organized storage vault that retrieves values on command."

        return Lesson(
            lesson_id=generate_id("lsn"),
            concept_id=concept.concept_id,
            learning_objective_id=objective.objective_id,
            title=f"Mastering {concept.name}",
            explanation=explanation,
            examples=examples,
            key_points=key_points,
            analogy=analogy,
            source_references=ref_ids,
        )
