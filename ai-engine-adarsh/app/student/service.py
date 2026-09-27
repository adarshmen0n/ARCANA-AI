"""Student Service managing persistent student learner state and interactions."""

import os
import sys
from typing import Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from shared.schemas.student_mastery import (
    ConceptMastery,
    MasteryUpdateResult,
    StudentProfile,
)
from app.core.errors import ResourceNotFoundException
from app.core.logging import get_logger
from app.mastery.engine import mastery_engine
from app.student.models import StudentInteractionRecord

logger = get_logger("app.student.service")


class StudentService:
    """Maintains student profiles, interaction history, and mastery states."""

    def __init__(self):
        self._students: Dict[str, StudentProfile] = {}
        self._interaction_history: Dict[str, List[StudentInteractionRecord]] = {}

    def get_or_create_student(self, student_id: str, display_name: str = "Learner") -> StudentProfile:
        """Retrieves existing student profile or creates a fresh one."""
        if student_id not in self._students:
            profile = StudentProfile(
                student_id=student_id,
                display_name=display_name,
                xp=0,
                level=1,
                knowledge_coins=0,
                concept_mastery={},
                completed_missions=[],
                weak_concepts=[],
                strong_concepts=[],
            )
            self._students[student_id] = profile
            self._interaction_history[student_id] = []
            logger.info(f"Initialized new student profile for '{student_id}' ({display_name})")
        return self._students[student_id]

    def get_student(self, student_id: str) -> StudentProfile:
        """Retrieves student profile. Raises ResourceNotFoundException if missing."""
        profile = self._students.get(student_id)
        if not profile:
            raise ResourceNotFoundException("StudentProfile", student_id)
        return profile

    def record_interaction(
        self,
        student_id: str,
        interaction: StudentInteractionRecord,
    ) -> MasteryUpdateResult:
        """Processes interaction, recalculates mastery, updates gamification stats, and adjusts profile."""
        profile = self.get_or_create_student(student_id)
        cid = interaction.concept_id

        # Get or initialize concept mastery record
        if cid not in profile.concept_mastery:
            profile.concept_mastery[cid] = ConceptMastery(
                concept_id=cid,
                mastery_score=0.0,
                total_attempts=0,
                successful_attempts=0,
                consecutive_correct=0,
                last_difficulty_solved=1,
            )

        current_record = profile.concept_mastery[cid]

        # Calculate mastery update via MasteryEngine
        update_result = mastery_engine.calculate_update(
            student_id=student_id,
            current_mastery=current_record,
            interaction=interaction,
        )

        # Update concept record stats
        current_record.mastery_score = update_result.new_score
        current_record.total_attempts += 1
        current_record.last_attempt_timestamp = interaction.timestamp

        if interaction.is_correct:
            current_record.successful_attempts += 1
            current_record.consecutive_correct += 1
            current_record.last_difficulty_solved = max(
                current_record.last_difficulty_solved, interaction.difficulty
            )

            # Award XP & coins (difficulty scaled)
            xp_gain = 50 * interaction.difficulty
            coins_gain = 10 * interaction.difficulty
            profile.xp += xp_gain
            profile.knowledge_coins += coins_gain

            # Level up progression (500 XP per level)
            profile.level = 1 + (profile.xp // 500)
        else:
            current_record.consecutive_correct = 0

        # Update weak and strong concept sets
        if current_record.mastery_score >= 0.8:
            if cid not in profile.strong_concepts:
                profile.strong_concepts.append(cid)
            if cid in profile.weak_concepts:
                profile.weak_concepts.remove(cid)
        elif current_record.mastery_score < 0.4:
            if cid not in profile.weak_concepts:
                profile.weak_concepts.append(cid)
            if cid in profile.strong_concepts:
                profile.strong_concepts.remove(cid)
        else:
            if cid in profile.weak_concepts:
                profile.weak_concepts.remove(cid)
            if cid in profile.strong_concepts:
                profile.strong_concepts.remove(cid)

        # Record into interaction log
        self._interaction_history[student_id].append(interaction)

        return update_result

    def list_students(self) -> List[StudentProfile]:
        return list(self._students.values())


# Global singleton instance
student_service = StudentService()
