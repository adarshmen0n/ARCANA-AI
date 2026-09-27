"""Adaptive Mission Sequencer coordinating Learning Graph, Student Profile, and Mission Generation."""

from typing import List, Optional
from shared.schemas.game_specification import GameSpecification
from app.student.service import student_service
from app.learning_graph.service import learning_graph_service
from app.knowledge.engine import knowledge_engine
from app.difficulty.engine import difficulty_engine
from app.generation.mission_generator import mission_generator
from app.core.logging import get_logger

logger = get_logger("app.sequencer.service")


class AdaptiveSequencer:
    """Dynamically sequences the next personalized GameSpecification mission for a learner."""

    def sequence_next_mission(
        self,
        student_id: str,
        document_id: str,
    ) -> GameSpecification:
        """Determines next optimal pedagogical challenge based on mastery state and curriculum DAG."""
        profile = student_service.get_or_create_student(student_id)

        # Determine mastered concepts (score >= 0.7)
        completed_concept_ids = [
            cid for cid, m in profile.concept_mastery.items() if m.mastery_score >= 0.7
        ]

        # Prioritize earliest weak concept if any exist
        weak_cid = profile.weak_concepts[0] if profile.weak_concepts else None

        # Query Learning Graph for next concept recommendation
        rec = learning_graph_service.recommend_next_concept(
            document_id=document_id,
            completed_concept_ids=completed_concept_ids,
            weak_concept_id=weak_cid,
        )

        target_node = rec.recommended_concept
        concept_id = target_node.concept_id

        # Find full Concept model from knowledge engine
        concept = None
        for c in knowledge_engine.get_concepts(document_id):
            if c.concept_id == concept_id:
                concept = c
                break

        if not concept:
            from app.knowledge.models import Concept
            concept = Concept(
                concept_id=concept_id,
                name=target_node.name,
                topic=target_node.topic,
                definition=target_node.definition,
                difficulty=target_node.difficulty,
            )

        # Look up student's current mastery on this specific concept
        mastery_record = profile.concept_mastery.get(concept_id)
        current_mastery = mastery_record.mastery_score if mastery_record else 0.0

        # Calibrate difficulty to student's live capability
        calibrated_diff = difficulty_engine.calculate_student_difficulty(
            content_difficulty=target_node.difficulty,
            student_mastery=current_mastery,
        )

        # If learner is remediating, ensure difficulty does not exceed baseline
        if rec.is_remediation:
            calibrated_diff = max(1, min(calibrated_diff, 2))

        # Check if student qualifies for a Boss Battle:
        # If all ready concepts are completed and overall score is high
        is_boss = False
        all_concepts = knowledge_engine.get_concepts(document_id)
        if all_concepts and len(completed_concept_ids) >= len(all_concepts) - 1:
            is_boss = True

        logger.info(
            f"Sequencer selected concept '{concept.name}' (id={concept_id}) for student '{student_id}'. "
            f"Calibrated difficulty: {calibrated_diff}, is_boss={is_boss}, remediation={rec.is_remediation}"
        )

        # Generate complete, validated GameSpecification
        return mission_generator.generate_mission(
            concept=concept,
            difficulty=calibrated_diff,
            is_boss=is_boss,
            document_id=document_id,
        )


adaptive_sequencer = AdaptiveSequencer()
