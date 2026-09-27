"""Telemetry Processing Subsystem translating GameEvents into student mastery updates."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from shared.schemas.game_event import GameEvent, GameEventType
from shared.schemas.student_mastery import MasteryUpdateResult
from app.student.service import student_service
from app.student.models import StudentInteractionRecord
from app.difficulty.engine import difficulty_engine
from app.core.logging import get_logger

logger = get_logger("app.telemetry.service")


class TelemetryProcessingResult(BaseModel):
    event_id: str
    event_type: GameEventType
    student_id: str
    concept_id: str
    mastery_updated: bool = False
    mastery_result: Optional[MasteryUpdateResult] = None
    xp_awarded: int = 0
    coins_awarded: int = 0
    current_level: int = 1
    feedback_message: str = "Telemetry recorded successfully."


class TelemetryService:
    """Processes incoming telemetry events from the Game Engine and updates learner profile."""

    def __init__(self):
        self._event_audit_log: List[GameEvent] = []

    def process_event(self, event: GameEvent) -> TelemetryProcessingResult:
        """Processes a GameEvent, updating student mastery and gamification state if applicable."""
        self._event_audit_log.append(event)
        logger.info(f"Processing GameEvent {event.event_id} ({event.event_type}) for student {event.student_id}")

        profile = student_service.get_or_create_student(event.student_id)

        # Handle Question Answered / Assessment attempts
        if event.event_type == GameEventType.QUESTION_ANSWERED:
            is_correct = bool(event.payload.is_correct)
            hints_used = event.payload.hints_used_count
            diff = event.payload.difficulty
            time_spent = event.payload.time_taken_seconds

            record = StudentInteractionRecord(
                student_id=event.student_id,
                concept_id=event.concept_id,
                difficulty=diff,
                is_correct=is_correct,
                time_taken_seconds=time_spent,
                hints_used=hints_used,
            )

            # Record interaction and calculate deterministic mastery update
            mastery_update = student_service.record_interaction(event.student_id, record)

            xp_gain = 50 * diff if is_correct else 10
            coins_gain = 10 * diff if is_correct else 0

            msg = (
                f"Victory! Correct answer on {event.concept_id}. "
                f"Mastery increased by {mastery_update.score_delta:+.2f}."
                if is_correct
                else f"Incorrect answer on {event.concept_id}. Review suggested."
            )

            if mastery_update.remediation_required:
                msg += " Remediation triggered: difficulty lowered for scaffolding."

            return TelemetryProcessingResult(
                event_id=event.event_id,
                event_type=event.event_type,
                student_id=event.student_id,
                concept_id=event.concept_id,
                mastery_updated=True,
                mastery_result=mastery_update,
                xp_awarded=xp_gain,
                coins_awarded=coins_gain,
                current_level=profile.level,
                feedback_message=msg,
            )

        # Handle Mission Completion
        elif event.event_type == GameEventType.MISSION_COMPLETED:
            if event.mission_id not in profile.completed_missions:
                profile.completed_missions.append(event.mission_id)
                bonus_xp = 100
                bonus_coins = 25
                profile.xp += bonus_xp
                profile.knowledge_coins += bonus_coins
                profile.level = 1 + (profile.xp // 500)
                logger.info(f"Mission {event.mission_id} completed by {event.student_id}. Level={profile.level}")
                return TelemetryProcessingResult(
                    event_id=event.event_id,
                    event_type=event.event_type,
                    student_id=event.student_id,
                    concept_id=event.concept_id,
                    xp_awarded=bonus_xp,
                    coins_awarded=bonus_coins,
                    current_level=profile.level,
                    feedback_message=f"Mission {event.mission_id} completed! Bonus rewards unlocked.",
                )

        # Handle Boss Completion
        elif event.event_type == GameEventType.BOSS_COMPLETED:
            bonus_xp = 300
            bonus_coins = 100
            profile.xp += bonus_xp
            profile.knowledge_coins += bonus_coins
            profile.level = 1 + (profile.xp // 500)
            return TelemetryProcessingResult(
                event_id=event.event_id,
                event_type=event.event_type,
                student_id=event.student_id,
                concept_id=event.concept_id,
                xp_awarded=bonus_xp,
                coins_awarded=bonus_coins,
                current_level=profile.level,
                feedback_message=f"Boss defeated on {event.concept_id}! Epic milestone achieved.",
            )

        # Default fallback for other event types (HINT_REQUESTED, MISSION_STARTED, etc.)
        return TelemetryProcessingResult(
            event_id=event.event_id,
            event_type=event.event_type,
            student_id=event.student_id,
            concept_id=event.concept_id,
            current_level=profile.level,
            feedback_message=f"Telemetry event {event.event_type.value} logged.",
        )

    def get_events_for_student(self, student_id: str) -> List[GameEvent]:
        """Retrieves historical events recorded for a student."""
        return [e for e in self._event_audit_log if e.student_id == student_id]


telemetry_service = TelemetryService()
