"""Concept-level Mastery Engine calculating continuous student proficiency."""

import logging
from typing import Dict, List, Optional
from schemas.personalization import ConceptMastery, StudentState, GameplayEvent
from schemas.base import current_utc_time

logger = logging.getLogger("arcana.personalization.mastery")


class MasteryEngine:
    """Updates concept-level mastery scores using multi-signal pedagogical telemetry."""

    ALPHA: float = 0.65  # Weight of historical mastery vs new event signal

    @classmethod
    def process_gameplay_event(cls, state: StudentState, event: GameplayEvent) -> StudentState:
        """Update student mastery and progression based on an incoming gameplay event."""
        cid = event.concept_id
        mastery = state.masteries.get(
            cid,
            ConceptMastery(concept_id=cid, mastery_score=0.0, attempts=0),
        )

        # Calculate performance signal for this event (0.0 to 1.0)
        base_signal = 1.0 if event.is_correct else 0.0

        # Penalize excessive hint reliance (up to 30% reduction)
        hint_penalty = min(0.3, event.hints_used * 0.1)
        performance_signal = max(0.0, base_signal - hint_penalty)

        # Speed adjustment: bonus for fluent answers (< 8s), slight penalty for very slow (> 45s)
        if event.is_correct and event.response_time_seconds < 8.0:
            performance_signal = min(1.0, performance_signal + 0.1)
        elif event.response_time_seconds > 45.0:
            performance_signal = max(0.0, performance_signal - 0.05)

        # Update mastery score via Exponential Moving Average
        if mastery.attempts == 0:
            new_score = performance_signal
        else:
            new_score = (cls.ALPHA * mastery.mastery_score) + ((1.0 - cls.ALPHA) * performance_signal)

        # Update metrics
        mastery.mastery_score = round(min(1.0, max(0.0, new_score)), 3)
        mastery.attempts += 1
        if event.is_correct:
            mastery.correct_attempts += 1
        mastery.hints_used += event.hints_used

        # Rolling average response time
        mastery.avg_response_time_seconds = round(
            (mastery.avg_response_time_seconds * (mastery.attempts - 1) + event.response_time_seconds)
            / mastery.attempts,
            1,
        )
        mastery.last_attempted = current_utc_time().isoformat()

        state.masteries[cid] = mastery

        # Update gamification progression
        if event.is_correct:
            state.total_xp += 20
            state.total_coins += 5
            if event.mission_id not in state.completed_mission_ids:
                state.completed_mission_ids.append(event.mission_id)

        # Level progression (100 XP per level)
        state.current_level = (state.total_xp // 100) + 1

        # Update weak concepts list
        state.weak_concept_ids = [
            c for c, m in state.masteries.items() if m.mastery_score < 0.55 and m.attempts >= 1
        ]
        state.last_updated = current_utc_time().isoformat()

        logger.debug(
            "Student '%s' concept '%s' mastery updated to %.3f (Level %d)",
            state.student_id,
            cid,
            mastery.mastery_score,
            state.current_level,
        )
        return state
