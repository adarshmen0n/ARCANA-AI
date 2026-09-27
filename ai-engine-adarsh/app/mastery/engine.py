"""Deterministic Mastery Engine implementing Section 11 statistical understanding estimation."""

import os
import sys

# Ensure shared schemas can be imported cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from shared.schemas.student_mastery import ConceptMastery, MasteryUpdateResult
from app.student.models import StudentInteractionRecord
from app.core.logging import get_logger

logger = get_logger("app.mastery.engine")


class MasteryEngine:
    """Estimates and updates concept mastery deterministically without probabilistic LLM hallucination."""

    @staticmethod
    def calculate_update(
        student_id: str,
        current_mastery: ConceptMastery,
        interaction: StudentInteractionRecord,
    ) -> MasteryUpdateResult:
        """Calculates updated mastery score based on difficulty, correctness, hints, and streaks."""
        prev_score = current_mastery.mastery_score
        diff = interaction.difficulty

        if interaction.is_correct:
            # Base gain proportional to challenge difficulty
            base_gain = 0.06 * (diff / 2.0)

            # Hint penalty (1 hint reduces gain by 20%, max penalty caps at 60% reduction)
            hint_multiplier = max(0.4, 1.0 - (0.2 * interaction.hints_used))

            # Streak multiplier (up to +25% bonus for consistent mastery)
            streak_bonus = min(0.25, 0.05 * current_mastery.consecutive_correct)
            streak_multiplier = 1.0 + streak_bonus

            delta = round(base_gain * hint_multiplier * streak_multiplier, 4)
            new_score = min(1.0, round(prev_score + delta, 4))
        else:
            # Incorrect penalty: larger drops if previous mastery was low or repeatedly failed
            base_drop = 0.12 * (1.0 - (prev_score * 0.2))
            delta = -round(base_drop, 4)
            new_score = max(0.0, round(prev_score + delta, 4))

        # Check remediation threshold (score dropped below 0.4 after multiple attempts)
        total_attempts = current_mastery.total_attempts + 1
        remediation_required = (new_score < 0.4) and (total_attempts >= 2)

        # Suggest next difficulty based on score brackets
        if new_score >= 0.8 and diff < 5:
            next_diff = diff + 1
        elif new_score < 0.4 and diff > 1:
            next_diff = diff - 1
        else:
            next_diff = diff

        logger.info(
            f"Mastery update for {student_id} on '{interaction.concept_id}': "
            f"{prev_score:.2f} -> {new_score:.2f} (delta={delta:+.4f}, remediation={remediation_required})"
        )

        return MasteryUpdateResult(
            student_id=student_id,
            concept_id=interaction.concept_id,
            previous_score=prev_score,
            new_score=new_score,
            score_delta=delta,
            remediation_required=remediation_required,
            suggested_next_difficulty=next_diff,
        )


mastery_engine = MasteryEngine()
