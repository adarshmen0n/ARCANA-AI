"""Unit and integration tests for deep cognitive subsystems: BKT + Ebbinghaus decay, misconception diagnosis, and Socratic depth."""

from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mastery.engine import mastery_engine
from app.mastery.diagnostic import diagnostic_engine, MisconceptionCategory
from app.tutor.service import ai_tutor_service, TutorQueryRequest
from app.student.service import student_service
from app.student.models import StudentInteractionRecord
from app.knowledge.models import Concept
from shared.schemas.student_mastery import ConceptMastery

client = TestClient(app)

SAMPLE_CONCEPT = Concept(
    concept_id="cpu_fcfs",
    name="First-Come First-Served Scheduling",
    topic="CPU Scheduling",
    definition="A non-preemptive algorithm executing tasks strictly in order of arrival.",
    difficulty=2,
)


def test_ebbinghaus_retention_decay():
    """Verify that Ebbinghaus forgetting curve decays mastery over elapsed days."""
    t0 = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    current = ConceptMastery(
        concept_id="cpu_fcfs",
        mastery_score=0.80,
        total_attempts=5,
        consecutive_correct=2,
        last_attempt_timestamp=t0,
    )
    # Apply decay with 7 days elapsed
    decayed = mastery_engine.apply_temporal_decay(current)
    assert decayed < 0.80
    assert decayed >= mastery_engine.DEFAULT_P_L0


def test_ebbinghaus_short_session_no_decay():
    """Verify that short elapsed times (< 1 hour) do not decay active learning sessions."""
    t_recent = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    current = ConceptMastery(
        concept_id="cpu_fcfs",
        mastery_score=0.80,
        total_attempts=5,
        consecutive_correct=2,
        last_attempt_timestamp=t_recent,
    )
    decayed = mastery_engine.apply_temporal_decay(current)
    assert decayed == 0.80


def test_misconception_diagnostic_engine_detection():
    """Verify diagnosis of cognitive fallacies on distractor selection."""
    diagnosis = diagnostic_engine.diagnose_response(
        concept=SAMPLE_CONCEPT,
        selected_option_id="B",
        correct_option_id="A",
        challenge_prompt="Why does FCFS cause convoy effect?",
        options=[{"id": "A", "text": "Head of queue blocks all"}, {"id": "B", "text": "Arrival order is always optimal"}],
    )
    assert diagnosis.is_correct is False
    assert diagnosis.category == MisconceptionCategory.INVARIANT_VIOLATION
    assert len(diagnosis.root_cause_explanation) > 15
    assert len(diagnosis.cognitive_conflict_prompt) > 10
    assert len(diagnosis.remedial_nudge) > 10


def test_misconception_diagnostic_engine_correct_response():
    """Verify diagnosis on correct selection confirms invariants."""
    diagnosis = diagnostic_engine.diagnose_response(
        concept=SAMPLE_CONCEPT,
        selected_option_id="A",
        correct_option_id="A",
        challenge_prompt="Core rule of FCFS",
        options=[{"id": "A", "text": "Order of arrival"}],
    )
    assert diagnosis.is_correct is True
    assert diagnosis.category is None
    assert "invariants" in diagnosis.root_cause_explanation.lower()


def test_socratic_tutor_adaptive_cognitive_depth():
    """Verify Socratic tutor adapts inquiry depth based on learner mastery."""
    # 1. Novice student (mastery 0.0) -> Scaffolded depth
    student_service.get_or_create_student("cadet_novice")
    res_novice = ai_tutor_service.ask_tutor(
        TutorQueryRequest(student_id="cadet_novice", concept_id="cpu_fcfs", query="What is FCFS?")
    )
    assert res_novice.cognitive_depth_level == "scaffolded"

    # 2. Master student (mastery 0.85) -> Advanced depth
    student_service.get_or_create_student("cadet_expert")
    expert_prof = student_service.get_student("cadet_expert")
    expert_prof.concept_mastery["cpu_fcfs"] = ConceptMastery(
        concept_id="cpu_fcfs",
        mastery_score=0.85,
        total_attempts=5,
        successful_attempts=5,
        consecutive_correct=5,
    )
    res_expert = ai_tutor_service.ask_tutor(
        TutorQueryRequest(student_id="cadet_expert", concept_id="cpu_fcfs", query="How does burst variance impact FCFS?")
    )
    assert res_expert.cognitive_depth_level == "advanced"
    assert "utilization" in res_expert.guiding_question.lower() or "process" in res_expert.guiding_question.lower()
