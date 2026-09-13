"""Learning Objective Generator anchored in Bloom's Taxonomy."""

from schemas.knowledge import Concept
from schemas.generation import LearningObjective
from schemas.base import generate_id
from .base import BaseGenerator


class ObjectiveGenerator(BaseGenerator):
    """Generates pedagogically anchored learning objectives for concepts."""

    def generate_objective(self, concept: Concept) -> LearningObjective:
        # Map difficulty to Bloom's taxonomy level
        bloom_map = {
            1: "remember",
            2: "understand",
            3: "apply",
            4: "analyze",
            5: "evaluate",
        }
        bloom_level = bloom_map.get(concept.difficulty, "understand")

        description = (
            f"Understand and apply principles of {concept.name} to solve foundational problems."
            if concept.difficulty <= 2
            else f"Analyze and evaluate {concept.name} behaviors and dependency trade-offs."
        )

        criteria = [
            f"Define what {concept.name} accomplishes.",
            f"Identify correct usage and common pitfalls of {concept.name}.",
            f"Solve practical challenges involving {concept.name}.",
        ]

        return LearningObjective(
            objective_id=generate_id("obj"),
            concept_id=concept.concept_id,
            description=description,
            bloom_level=bloom_level,
            success_criteria=criteria,
        )
