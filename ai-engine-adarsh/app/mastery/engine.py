"""Deterministic Mastery Engine implementing Bayesian Knowledge Tracing (BKT) and adaptive calibration."""

import os
import sys
from typing import Optional

# Ensure shared schemas can be imported cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from shared.schemas.student_mastery import ConceptMastery, MasteryUpdateResult
from app.student.models import StudentInteractionRecord
from app.core.logging import get_logger

logger = get_logger("app.mastery.engine")


class BayesianKnowledgeTracingEngine:
    """Implements Corbett & Anderson Bayesian Knowledge Tracing (BKT) with adaptive hint & streak scaling."""

    # Default BKT hyperparameters
    DEFAULT_P_L0 = 0.10   # Prior probability of knowing concept
    BASE_P_T = 0.12       # Base learning/transition probability
    BASE_P_G = 0.25       # Base probability of guessing correctly (4-choice MCQ)
    BASE_P_S = 0.10       # Base probability of slip (careless mistake despite knowing)

    @classmethod
    def calculate_update(
        cls,
        student_id: str,
        current_mastery: ConceptMastery,
        interaction: StudentInteractionRecord,
    ) -> MasteryUpdateResult:
        """Calculates Bayesian posterior probability of knowledge acquisition after student interaction."""
        prev_score = current_mastery.mastery_score
        # If student has zero prior attempts, initialize with BKT prior P(L0)
        p_prior = prev_score if (current_mastery.total_attempts > 0 or prev_score > 0.0) else cls.DEFAULT_P_L0
        diff = max(1, min(5, interaction.difficulty))

        # 1. Calibrate Guess Probability P(G) based on Hints used
        # Using hints increases effective guess/scaffold probability, reducing evidence of mastery
        p_g = min(0.75, cls.BASE_P_G + (0.15 * interaction.hints_used))

        # 2. Calibrate Slip Probability P(S) based on Difficulty and Response Time
        p_s = cls.BASE_P_S
        if diff >= 4:
            p_s += 0.04  # Higher difficulty increases slip likelihood

        # 3. Compute Posterior Probability P(L_t | Observation)
        if interaction.is_correct:
            # P(L|correct) = (P(L) * (1 - P(S))) / [P(L) * (1 - P(S)) + (1 - P(L)) * P(G)]
            num = p_prior * (1.0 - p_s)
            den = num + ((1.0 - p_prior) * p_g)
            p_posterior = num / den if den > 0 else p_prior

            # Transition step: P(L_t+1) = P(L_t) + (1 - P(L_t)) * P(T)
            p_t = cls.BASE_P_T + (0.03 * (diff - 1))
            new_p = p_posterior + ((1.0 - p_posterior) * p_t)

            # Streak multiplier (up to +25% bonus on the gain)
            streak_bonus = min(0.25, 0.05 * current_mastery.consecutive_correct)
            gain = (new_p - p_prior) * (1.0 + streak_bonus)
            new_score = round(min(1.0, p_prior + gain), 4)

            # Ensure strict monotonically positive delta on correct answer
            if new_score <= prev_score:
                new_score = min(1.0, round(prev_score + 0.02, 4))
            delta = round(new_score - prev_score, 4)

        else:
            # P(L|incorrect) = (P(L) * P(S)) / [P(L) * P(S) + (1 - P(L)) * (1 - P(G))]
            num = p_prior * p_s
            den = num + ((1.0 - p_prior) * (1.0 - p_g))
            p_posterior = num / den if den > 0 else 0.0

            # On failure, no positive transition occurs; score drops to posterior
            new_score = round(max(0.0, p_posterior), 4)

            # Ensure strict negative delta on failure
            if new_score >= prev_score:
                drop = 0.10 * (1.0 - (prev_score * 0.2))
                new_score = max(0.0, round(prev_score - drop, 4))
            delta = round(new_score - prev_score, 4)

        # 4. Remediation condition (score dropped below 0.40 after multiple attempts)
        total_attempts = current_mastery.total_attempts + 1
        remediation_required = (new_score < 0.40) and (total_attempts >= 2)

        # 5. Adaptive Difficulty Recommendation
        if new_score >= 0.80 and diff < 5:
            next_diff = diff + 1
        elif new_score < 0.40 and diff > 1:
            next_diff = diff - 1
        else:
            next_diff = diff

        logger.info(
            f"[BKT Mastery] Student '{student_id}' on '{interaction.concept_id}': "
            f"{prev_score:.4f} -> {new_score:.4f} (delta={delta:+.4f}, BKT_p_g={p_g:.2f}, remediation={remediation_required})"
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


# Export alias and global singleton for backward compatibility
MasteryEngine = BayesianKnowledgeTracingEngine
mastery_engine = BayesianKnowledgeTracingEngine()
