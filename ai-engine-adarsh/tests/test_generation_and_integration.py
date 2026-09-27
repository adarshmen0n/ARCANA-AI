"""Comprehensive integration and unit tests for Generation, GameSpecification, Telemetry, Sequencer, and Tutor subsystems."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.knowledge.models import Concept
from app.generation.lesson_generator import lesson_generator
from app.generation.question_generator import question_generator
from app.generation.hint_generator import hint_generator
from app.generation.npc_generator import npc_generator
from app.generation.boss_generator import boss_generator
from app.generation.mission_generator import mission_generator
from app.generation.models import NPCPersona
from app.telemetry.service import telemetry_service
from app.sequencer.service import adaptive_sequencer
from app.tutor.service import ai_tutor_service, TutorQueryRequest
from app.student.service import student_service
from app.ingestion.service import ingestion_service
from app.chunking.service import chunking_service
from app.knowledge.engine import knowledge_engine
from shared.schemas.game_specification import GameSpecification
from shared.schemas.game_event import GameEvent, GameEventType, EventPayload

client = TestClient(app)

SAMPLE_CONCEPT = Concept(
    concept_id="cpu_fcfs",
    name="First-Come First-Served Scheduling",
    topic="CPU Scheduling",
    definition="A non-preemptive algorithm where the process that requests the CPU first is allocated the CPU first.",
    difficulty=2,
    common_misconceptions=["Assuming FCFS is always fast because of low scheduling overhead."],
)


def test_hint_generator_tiers():
    """Verify that hint generator generates 3 tiers: nudge, guidance, and scaffold."""
    hints = hint_generator.generate_progressive_hints(
        concept=SAMPLE_CONCEPT,
        prompt="What is the average waiting time?",
        correct_answer_summary="processes run in order of arrival",
        difficulty=2,
    )
    assert len(hints) == 3
    assert hints[0].level == 1 and hints[0].type == "nudge"
    assert hints[1].level == 2 and hints[1].type == "guidance"
    assert hints[2].level == 3 and hints[2].type == "scaffold"
    for h in hints:
        assert len(h.text) > 10


def test_lesson_generator():
    """Verify lesson generation structure and content."""
    lesson = lesson_generator.generate_lesson(SAMPLE_CONCEPT, difficulty=2)
    assert lesson.concept_id == "cpu_fcfs"
    assert len(lesson.story_hook) > 10
    assert len(lesson.core_explanation) > 10
    assert len(lesson.analogy) > 10
    assert len(lesson.key_takeaways) >= 2
    assert len(lesson.common_misconceptions) >= 1


def test_question_generator_and_validation():
    """Verify question generation produces valid options, correct option id, and hints."""
    q = question_generator.generate_question(SAMPLE_CONCEPT, difficulty=3)
    assert q.concept_id == "cpu_fcfs"
    assert len(q.options) >= 2
    option_ids = {opt.id for opt in q.options}
    assert q.correct_option_id in option_ids
    assert len(q.hints) == 3
    assert len(q.explanation) > 10


def test_npc_generator_personas():
    """Verify NPC dialogue and lore for distinct personas."""
    alan = npc_generator.generate_npc_payload(SAMPLE_CONCEPT, persona=NPCPersona.ARCHMAGE_ALAN)
    assert alan.npc_id == "archmage_alan"
    assert len(alan.dialogue) >= 3

    warden = npc_generator.generate_npc_payload(SAMPLE_CONCEPT, persona=NPCPersona.CHRONOS_WARDEN)
    assert warden.npc_id == "chronos_warden"
    assert any("millisecond" in line.lower() or "clock" in line.lower() for line in warden.dialogue)

    sprite = npc_generator.generate_npc_payload(SAMPLE_CONCEPT, persona=NPCPersona.GLITCH_SPRITE)
    assert sprite.npc_id == "glitch_sprite"


def test_boss_generator_encounter():
    """Verify multi-phase boss battle construction."""
    encounter = boss_generator.generate_full_encounter(SAMPLE_CONCEPT, phases=3)
    assert encounter.phases == 3
    assert encounter.hp == 300
    assert encounter.shield_weakness_concept == "cpu_fcfs"
    assert len(encounter.challenges) == 3


def test_mission_generator_valid_game_specification():
    """Verify full GameSpecification contract compliance."""
    spec = mission_generator.generate_mission(
        concept=SAMPLE_CONCEPT,
        difficulty=3,
        is_boss=False,
    )
    assert isinstance(spec, GameSpecification)
    assert spec.version == "1.0.0"
    assert spec.concept_id == "cpu_fcfs"
    assert spec.difficulty == 3
    assert spec.challenge.correct_option_id in {opt.id for opt in spec.challenge.options}
    assert spec.reward.xp == 300
    assert spec.boss.is_boss_mission is False


def test_telemetry_service_question_and_mastery():
    """Verify that GameEvent ingestion updates student mastery and awards rewards."""
    event = GameEvent(
        event_id="evt_test_001",
        student_id="student_telemetry_1",
        session_id="sess_123",
        mission_id="MSN-CPU-001",
        concept_id="cpu_fcfs",
        event_type=GameEventType.QUESTION_ANSWERED,
        payload=EventPayload(
            challenge_id="q_1",
            selected_option_id="A",
            is_correct=True,
            difficulty=3,
            time_taken_seconds=14.0,
            hints_used_count=1,
        ),
        client_timestamp="2026-09-27T12:00:00Z",
    )
    res = telemetry_service.process_event(event)
    assert res.mastery_updated is True
    assert res.mastery_result.new_score > 0
    assert res.xp_awarded == 150  # 50 * diff 3

    # Check student profile
    profile = student_service.get_student("student_telemetry_1")
    assert profile.xp >= 150
    assert "cpu_fcfs" in profile.concept_mastery


def test_telemetry_mission_completion_bonus():
    """Verify mission completion bonus awards."""
    event = GameEvent(
        event_id="evt_test_002",
        student_id="student_telemetry_1",
        session_id="sess_123",
        mission_id="MSN-CPU-001",
        concept_id="cpu_fcfs",
        event_type=GameEventType.MISSION_COMPLETED,
        payload=EventPayload(),
        client_timestamp="2026-09-27T12:05:00Z",
    )
    res = telemetry_service.process_event(event)
    assert res.xp_awarded == 100
    assert res.coins_awarded == 25


def test_ai_tutor_socratic_response():
    """Verify AI Tutor produces guiding questions and pedagogical feedback."""
    req = TutorQueryRequest(
        student_id="student_tutor_1",
        concept_id="cpu_fcfs",
        query="Why does FCFS have high average waiting time?",
    )
    resp = ai_tutor_service.ask_tutor(req)
    assert resp.student_id == "student_tutor_1"
    assert len(resp.reply) > 20
    assert len(resp.guiding_question) > 10
    assert len(resp.suggested_action) > 10


def test_end_to_end_api_endpoints():
    """Integration test verifying all new FastAPI v1 routes."""
    # 1. Lesson generation
    res = client.post("/api/v1/generation/lesson", json={"concept_id": "cpu_fcfs", "difficulty": 2})
    assert res.status_code == 200
    assert "story_hook" in res.json()

    # 2. Question generation
    res = client.post("/api/v1/generation/question", json={"concept_id": "cpu_fcfs", "difficulty": 2})
    assert res.status_code == 200
    assert "correct_option_id" in res.json()

    # 3. Boss generation
    res = client.post("/api/v1/generation/boss", json={"concept_id": "cpu_fcfs", "phases": 2})
    assert res.status_code == 200
    assert res.json()["hp"] == 200

    # 4. GameSpecification generation
    res = client.post("/api/v1/game-spec/generate", json={"concept_id": "cpu_fcfs", "difficulty": 3})
    assert res.status_code == 200
    spec_data = res.json()
    assert spec_data["version"] == "1.0.0"
    assert spec_data["difficulty"] == 3

    # 5. Telemetry event submission
    event_payload = {
        "version": "1.0.0",
        "event_id": "evt_api_test_99",
        "student_id": "api_student",
        "session_id": "sess_api",
        "mission_id": "MSN-TEST",
        "concept_id": "cpu_fcfs",
        "event_type": "QUESTION_ANSWERED",
        "payload": {
            "is_correct": True,
            "difficulty": 2,
            "hints_used_count": 0,
        },
        "client_timestamp": "2026-09-27T12:00:00Z",
    }
    res = client.post("/api/v1/telemetry/events", json=event_payload)
    assert res.status_code == 200
    assert res.json()["mastery_updated"] is True

    # 6. Socratic tutor query
    tutor_payload = {
        "student_id": "api_student",
        "concept_id": "cpu_fcfs",
        "query": "How does convoy effect happen?",
    }
    res = client.post("/api/v1/tutor/ask", json=tutor_payload)
    assert res.status_code == 200
    assert "guiding_question" in res.json()
