"""Generator for Bloom's Taxonomy learning objectives tied to concepts and difficulty levels."""

from typing import Dict, List, Optional
from app.knowledge.models import Concept
from app.objectives.models import BloomTaxonomyLevel, LearningObjective, ConceptObjectivesResult
from app.core.logging import get_logger

logger = get_logger("app.objectives.generator")

DIFFICULTY_TO_BLOOM: Dict[int, BloomTaxonomyLevel] = {
    1: BloomTaxonomyLevel.REMEMBER,
    2: BloomTaxonomyLevel.UNDERSTAND,
    3: BloomTaxonomyLevel.APPLY,
    4: BloomTaxonomyLevel.ANALYZE,
    5: BloomTaxonomyLevel.EVALUATE,
}

BLOOM_ACTION_VERBS: Dict[BloomTaxonomyLevel, List[str]] = {
    BloomTaxonomyLevel.REMEMBER: ["define", "identify", "recall", "list", "name", "state"],
    BloomTaxonomyLevel.UNDERSTAND: ["explain", "summarize", "describe", "classify", "interpret", "clarify"],
    BloomTaxonomyLevel.APPLY: ["calculate", "demonstrate", "execute", "solve", "implement", "simulate"],
    BloomTaxonomyLevel.ANALYZE: ["differentiate", "examine", "compare", "diagnose", "deconstruct", "contrast"],
    BloomTaxonomyLevel.EVALUATE: ["assess", "critique", "justify", "recommend", "appraise", "defend"],
    BloomTaxonomyLevel.CREATE: ["design", "formulate", "construct", "synthesize", "architect"],
}


class ObjectiveGenerator:
    """Generates pedagogical learning objectives aligned with Bloom's Taxonomy."""

    def generate_for_difficulty(
        self,
        concept: Concept,
        difficulty: int,
    ) -> LearningObjective:
        """Generates a single Bloom's taxonomy objective for a concept at a given difficulty (1-5)."""
        difficulty = max(1, min(5, difficulty))
        bloom_level = DIFFICULTY_TO_BLOOM.get(difficulty, BloomTaxonomyLevel.UNDERSTAND)
        verbs = BLOOM_ACTION_VERBS[bloom_level]

        statements = {
            BloomTaxonomyLevel.REMEMBER: f"Identify and state the foundational definition of {concept.name}.",
            BloomTaxonomyLevel.UNDERSTAND: f"Explain how {concept.name} functions and summarize its core operational purpose.",
            BloomTaxonomyLevel.APPLY: f"Apply principles of {concept.name} to solve concrete computational or workflow problems.",
            BloomTaxonomyLevel.ANALYZE: f"Analyze trade-offs, structural dependencies, and edge cases related to {concept.name}.",
            BloomTaxonomyLevel.EVALUATE: f"Evaluate systemic trade-offs involving {concept.name} and justify optimal choices under constraints.",
            BloomTaxonomyLevel.CREATE: f"Design and architect an optimal solution utilizing {concept.name}.",
        }

        criteria = {
            BloomTaxonomyLevel.REMEMBER: f"Accurately recalls definitions and terminology for {concept.name} without hints.",
            BloomTaxonomyLevel.UNDERSTAND: f"Explains concepts in learner's own words and classifies correct use cases.",
            BloomTaxonomyLevel.APPLY: f"Executes correct calculations and algorithmic steps in scenarios testing {concept.name}.",
            BloomTaxonomyLevel.ANALYZE: f"Identifies pitfalls, compares alternatives, and diagnoses errors in scenarios involving {concept.name}.",
            BloomTaxonomyLevel.EVALUATE: f"Defends architectural decisions and critiques suboptimal implementations of {concept.name}.",
            BloomTaxonomyLevel.CREATE: f"Constructs end-to-end designs demonstrating master-level mastery.",
        }

        return LearningObjective(
            concept_id=concept.concept_id,
            bloom_level=bloom_level,
            difficulty=difficulty,
            statement=statements[bloom_level],
            action_verbs=verbs[:3],
            success_criteria=criteria[bloom_level],
        )

    def generate_objectives_for_concept(
        self,
        concept: Concept,
        difficulties: Optional[List[int]] = None,
    ) -> ConceptObjectivesResult:
        """Generates comprehensive multi-tiered learning objectives for a concept."""
        if not difficulties:
            difficulties = [1, 2, 3, 4, 5]

        objectives = [self.generate_for_difficulty(concept, d) for d in difficulties]

        return ConceptObjectivesResult(
            concept_id=concept.concept_id,
            concept_name=concept.name,
            objectives=objectives,
            total_objectives=len(objectives),
        )


objective_generator = ObjectiveGenerator()
