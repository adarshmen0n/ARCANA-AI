"""Unit and integration tests for Student, Mastery, Difficulty, and Objectives subsystems."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mastery.engine import mastery_engine
from app.difficulty.engine import difficulty_engine
from app.student.service import student_service
from app.student.models import StudentInteractionRecord
from app.objectives.generator import objective_generator
from app.objectives.models import BloomTaxonomyLevel
from app.knowledge.models import Concept
from shared.schemas.student_mastery import ConceptMastery

client = TestClient(app)


def test_mastery_engine_correct_answer_gain():
    """Test that correct answers yield positive score delta with difficulty scaling."""
    current = ConceptMastery(concept_id="cpu_fcfs", mastery_score=0.2)
    record = StudentInteractionRecord(
        student_id="student_101",
        concept_id="cpu_fcfs",
        difficulty=3,
        is_correct=True,
        hints_used=0,
    )
    result = mastery_engine.calculate_update("student_101", current, record)
    assert result.score_delta > 0
    assert result.new_score > current.mastery_score
    assert result.new_score <= 1.0


def test_mastery_engine_hint_penalty_and_streak_bonus():
    """Test that hints penalize gains and consecutive streaks boost gains."""
    current = ConceptMastery(concept_id="cpu_fcfs", mastery_score=0.5, consecutive_correct=0)
    
    # 0 hints
    rec_no_hints = StudentInteractionRecord(
        student_id="student_101",
        concept_id="cpu_fcfs",
        difficulty=3,
        is_correct=True,
        hints_used=0,
    )
    res_no_hints = mastery_engine.calculate_update("student_101", current, rec_no_hints)

    # 2 hints
    rec_with_hints = StudentInteractionRecord(
        student_id="student_101",
        concept_id="cpu_fcfs",
        difficulty=3,
        is_correct=True,
        hints_used=2,
    )
    res_with_hints = mastery_engine.calculate_update("student_101", current, rec_with_hints)

    assert res_no_hints.score_delta > res_with_hints.score_delta

    # With streak of 3
    current_with_streak = ConceptMastery(concept_id="cpu_fcfs", mastery_score=0.5, consecutive_correct=3)
    res_streak = mastery_engine.calculate_update("student_101", current_with_streak, rec_no_hints)
    assert res_streak.score_delta > res_no_hints.score_delta


def test_mastery_engine_incorrect_drop_and_remediation():
    """Test that incorrect answers lower score and trigger remediation after repeated failures."""
    current = ConceptMastery(concept_id="cpu_fcfs", mastery_score=0.35, total_attempts=2)
    record = StudentInteractionRecord(
        student_id="student_101",
        concept_id="cpu_fcfs",
        difficulty=3,
        is_correct=False,
    )
    result = mastery_engine.calculate_update("student_101", current, record)
    assert result.score_delta < 0
    assert result.new_score < 0.35
    assert result.remediation_required is True
    assert result.suggested_next_difficulty < 3


def test_difficulty_engine_content_and_student_difficulty():
    """Test intrinsic content difficulty and dynamic student-calibrated difficulty."""
    concept_easy = Concept(
        concept_id="intro",
        name="Intro to Operating Systems",
        topic="OS",
        definition="Basic definition and overview of OS.",
        difficulty=1,
    )
    diff_easy = difficulty_engine.calculate_content_difficulty(concept_easy, prerequisite_count=0)
    assert diff_easy <= 2

    concept_hard = Concept(
        concept_id="deadlock",
        name="Deadlock Avoidance Banker's Algorithm",
        topic="OS",
        definition="Complex trade-offs and preemption in deadlock avoidance.",
        difficulty=4,
    )
    diff_hard = difficulty_engine.calculate_content_difficulty(concept_hard, prerequisite_count=4)
    assert diff_hard >= 4

    # Calibrated student difficulty
    # Low mastery drops difficulty by 1
    assert difficulty_engine.calculate_student_difficulty(3, student_mastery=0.2) == 2
    # Medium mastery keeps difficulty same
    assert difficulty_engine.calculate_student_difficulty(3, student_mastery=0.6) == 3
    # High mastery advances difficulty by 1
    assert difficulty_engine.calculate_student_difficulty(3, student_mastery=0.85) == 4


def test_objective_generator_bloom_taxonomy():
    """Test generation of Bloom's Taxonomy learning objectives across difficulty tiers."""
    concept = Concept(
        concept_id="fcfs",
        name="First-Come First-Served Scheduling",
        topic="CPU Scheduling",
        definition="Processes are dispatched according to arrival time.",
    )
    res = objective_generator.generate_objectives_for_concept(concept)
    assert res.total_objectives == 5
    levels = [obj.bloom_level for obj in res.objectives]
    assert levels == [
        BloomTaxonomyLevel.REMEMBER,
        BloomTaxonomyLevel.UNDERSTAND,
        BloomTaxonomyLevel.APPLY,
        BloomTaxonomyLevel.ANALYZE,
        BloomTaxonomyLevel.EVALUATE,
    ]
    for obj in res.objectives:
        assert len(obj.action_verbs) > 0
        assert len(obj.statement) > 10
        assert len(obj.success_criteria) > 10


def test_student_api_endpoints():
    """Integration test for /students endpoints and mastery tracking."""
    # 1. Create student
    res = client.post("/api/v1/students", json={"student_id": "alice_001", "display_name": "Alice"})
    assert res.status_code == 200
    data = res.json()
    assert data["student_id"] == "alice_001"
    assert data["xp"] == 0
    assert data["level"] == 1

    # 2. Record an interaction
    interaction_payload = {
        "student_id": "alice_001",
        "concept_id": "fcfs",
        "difficulty": 2,
        "is_correct": True,
        "time_taken_seconds": 12.5,
        "hints_used": 0,
    }
    res_interaction = client.post("/api/v1/students/alice_001/interaction", json=interaction_payload)
    assert res_interaction.status_code == 200
    int_data = res_interaction.json()
    assert int_data["new_score"] > 0
    assert int_data["score_delta"] > 0

    # 3. Check updated profile
    res_profile = client.get("/api/v1/students/alice_001")
    assert res_profile.status_code == 200
    pdata = res_profile.json()
    assert pdata["xp"] == 100  # 50 * difficulty 2
    assert "fcfs" in pdata["concept_mastery"]

    # 4. Query adaptive difficulty
    res_diff = client.get("/api/v1/students/alice_001/adaptive-difficulty/fcfs?content_difficulty=3")
    assert res_diff.status_code == 200
    ddata = res_diff.json()
    assert "recommended_difficulty" in ddata


def test_objectives_api_endpoint():
    """Integration test for /objectives/generate endpoint."""
    res = client.post(
        "/api/v1/objectives/generate",
        json={"concept_id": "round_robin", "concept_name": "Round Robin Scheduling", "difficulties": [1, 3, 5]},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_objectives"] == 3
    bloom_levels = [obj["bloom_level"] for obj in data["objectives"]]
    assert bloom_levels == ["remember", "apply", "evaluate"]
