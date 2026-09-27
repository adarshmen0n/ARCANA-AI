"""Difficulty Engine separating intrinsic Content Difficulty from adaptive Student Difficulty."""

from typing import Dict
from app.knowledge.models import Concept

DIFFICULTY_LABELS: Dict[int, str] = {
    1: "Very Easy",
    2: "Easy",
    3: "Medium",
    4: "Hard",
    5: "Very Hard",
}


class DifficultyEngine:
    """Calculates intrinsic concept difficulty and dynamic, personalized learner difficulty."""

    @staticmethod
    def calculate_content_difficulty(concept: Concept, prerequisite_count: int = 0) -> int:
        """Determines static curriculum difficulty based on abstraction and prerequisite burden."""
        score = 2  # Baseline Easy/Medium

        # Prerequisite weight: more prerequisites increase intrinsic complexity
        if prerequisite_count >= 3:
            score += 2
        elif prerequisite_count >= 1:
            score += 1

        # Textual complexity indicators
        desc = (concept.definition + " " + concept.name).lower()
        if any(term in desc for term in ("complex", "trade-off", "preemption", "inversion", "multilevel", "deadlock")):
            score += 1
        if any(term in desc for term in ("basic", "intro", "definition", "overview")):
            score -= 1

        return max(1, min(5, score))

    @staticmethod
    def calculate_student_difficulty(content_difficulty: int, student_mastery: float) -> int:
        """Calculates adaptive difficulty calibrated to an individual student's mastery.

        - Mastery >= 0.8: Advance difficulty by +1 (up to 5)
        - 0.4 <= Mastery < 0.8: Match intrinsic content difficulty
        - Mastery < 0.4: Lower difficulty by -1 (down to 1) for pedagogical scaffolding
        """
        if student_mastery >= 0.8:
            return min(5, content_difficulty + 1)
        elif student_mastery < 0.4:
            return max(1, content_difficulty - 1)
        else:
            return content_difficulty

    @staticmethod
    def get_difficulty_label(level: int) -> str:
        """Returns human-readable difficulty label."""
        return DIFFICULTY_LABELS.get(level, "Medium")


difficulty_engine = DifficultyEngine()
