"""Progressive 4-Tier Hint Generator."""

from typing import List
from schemas.generation import Hint, Question
from schemas.base import generate_id
from .base import BaseGenerator


class HintGenerator(BaseGenerator):
    """Generates 4-tier progressive scaffolding hints for questions."""

    def generate_progressive_hints(self, question: Question) -> List[Hint]:
        # Tier 1: Conceptual reminder
        h1 = Hint(
            hint_id=generate_id("hnt"),
            question_id=question.question_id,
            tier=1,
            text=f"Recall the fundamental definition and purpose of this concept.",
        )
        # Tier 2: Directional clue
        h2 = Hint(
            hint_id=generate_id("hnt"),
            question_id=question.question_id,
            tier=2,
            text=f"Focus on how this concept affects state and execution flow.",
        )
        # Tier 3: Stronger clue
        h3 = Hint(
            hint_id=generate_id("hnt"),
            question_id=question.question_id,
            tier=3,
            text=f"Eliminate options that contradict the concept's core purpose.",
        )
        # Tier 4: Near-answer assistance
        h4 = Hint(
            hint_id=generate_id("hnt"),
            question_id=question.question_id,
            tier=4,
            text=f"Review the first key principle: '{question.explanation[:80]}...'",
        )

        return [h1, h2, h3, h4]
