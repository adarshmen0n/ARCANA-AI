"""Difficulty Engine: Content Difficulty vs. Learner Difficulty modeling.

Differentiates intrinsic concept complexity from empirical student struggle,
calibrating challenges on a 1-5 pedagogical scale.
"""

from typing import Optional
from schemas.learning_graph import LearningGraphNode
from schemas.personalization import ConceptMastery


class DifficultyEngine:
    """Calculates objective content difficulty and adaptive learner difficulty."""

    @staticmethod
    def calculate_content_difficulty(node: LearningGraphNode) -> int:
        """Compute objective content difficulty (1=Beginner to 5=Expert).

        Considers prerequisite depth, number of dependencies, and inherent complexity.
        """
        score = node.difficulty

        # Deep DAG positions require higher cognitive integration
        if node.depth >= 3:
            score += 1
        if len(node.prerequisite_ids) >= 3:
            score += 1

        return min(5, max(1, score))

    @staticmethod
    def calculate_learner_difficulty(
        base_difficulty: int,
        mastery: Optional[ConceptMastery],
    ) -> int:
        """Compute empirical difficulty experienced by a specific learner.

        Adjusts content difficulty based on mastery, hint reliance, and error rates.
        """
        if not mastery or mastery.attempts == 0:
            return base_difficulty

        # If student has strong mastery (>0.85) with minimal hints, perceived difficulty is lower
        if mastery.mastery_score >= 0.85 and mastery.hints_used <= 1:
            return max(1, base_difficulty - 1)

        # If student struggles (mastery < 0.5 or high hints per attempt), perceived difficulty is higher
        hints_per_attempt = mastery.hints_used / max(1, mastery.attempts)
        if mastery.mastery_score < 0.5 or hints_per_attempt >= 2.0:
            return min(5, base_difficulty + 1)

        return base_difficulty
