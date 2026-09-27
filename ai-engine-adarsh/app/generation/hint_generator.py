"""Progressive Hint Generator creating 3-tier scaffolding hints."""

from typing import List, Optional
from shared.schemas.game_specification import ProgressiveHint
from app.knowledge.models import Concept
from app.core.logging import get_logger

logger = get_logger("app.generation.hint_generator")


class HintGenerator:
    """Generates 3-tiered progressive hints according to Section 17 of ARCANA architecture."""

    @staticmethod
    def generate_progressive_hints(
        concept: Concept,
        prompt: str,
        correct_answer_summary: str,
        difficulty: int = 2,
    ) -> List[ProgressiveHint]:
        """Produces 3 pedagogical hints: 1 (nudge), 2 (guidance), 3 (scaffold)."""
        # Tier 1: Nudge - Focuses attention on the underlying principle
        nudge_text = (
            f"Think about the core rule of {concept.name}: what determines priority or order in this system?"
            if "scheduling" in concept.name.lower() or "algorithm" in concept.name.lower()
            else f"Recall the foundational definition of {concept.name}. Consider its primary purpose."
        )

        # Tier 2: Guidance - Points out specific mechanisms, formulas, or trade-offs
        guidance_text = (
            f"Consider how {concept.name} handles incoming tasks. Does it use arrival times, bursts, or time slices? "
            f"Check if preemption is allowed."
            if "scheduling" in concept.name.lower()
            else f"Examine the key characteristics: {concept.definition[:100]}..."
        )

        # Tier 3: Scaffold - Concrete elimination and direct reasoning path
        scaffold_text = (
            f"Key takeaway: In {concept.name}, {correct_answer_summary}. "
            f"Eliminate options that contradict this operational behavior."
        )

        hints = [
            ProgressiveHint(
                level=1,
                type="nudge",
                text=nudge_text,
            ),
            ProgressiveHint(
                level=2,
                type="guidance",
                text=guidance_text,
            ),
            ProgressiveHint(
                level=3,
                type="scaffold",
                text=scaffold_text,
            ),
        ]

        logger.debug(f"Generated 3 progressive hints for concept {concept.concept_id}")
        return hints


hint_generator = HintGenerator()
