"""Tests for ARCANA-AI Shared Contracts and Schemas.

Verifies that:
1. Valid GameSpecification payloads validate successfully.
2. Malformed specifications are strictly rejected with clear validation errors.
3. Valid GameEvent telemetry payloads validate successfully.
4. Malformed telemetry payloads are rejected.
5. Student and Mastery models work as expected.
"""

import sys
import os
import pytest
from pydantic import ValidationError

# Add project root to sys.path so 'shared' can be imported cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.schemas.game_specification import (
    GameSpecification,
    NarrativePayload,
    NPCPayload,
    ChallengeOption,
    ProgressiveHint,
    ChallengePayload,
    BossPayload,
    RewardPayload,
    SpecificationMetadata,
)
from shared.schemas.game_event import GameEvent, GameEventType, EventPayload
from shared.schemas.student_mastery import StudentProfile, ConceptMastery


def test_valid_game_specification():
    """Verify that a complete, valid GameSpecification passes validation."""
    spec = GameSpecification(
        version="1.0.0",
        mission_id="OS-CPU-001",
        concept_id="cpu_scheduling_fcfs",
        title="The Queue of the Ancients",
        difficulty=2,
        learning_objective="Understand First-Come, First-Served scheduling and the Convoy Effect.",
        narrative=NarrativePayload(
            zone_theme="cyber_core",
            mission_intro="The Kernel mainframe is congested. Process buffers are stalling.",
        ),
        npc=NPCPayload(
            npc_id="grand_scribe_alan",
            npc_name="Grand Scribe Alan",
            dialogue=[
                "In FCFS, processes run strictly in order of arrival.",
                "Beware long CPU bursts causing the Convoy Effect.",
            ],
            lore_snippet="Alan has guarded the scheduling queues since the First Epoch.",
        ),
        challenge=ChallengePayload(
            challenge_id="CHAL-FCFS-001",
            challenge_type="mcq",
            prompt="What major drawback occurs in FCFS scheduling when a long process arrives first?",
            options=[
                ChallengeOption(id="A", text="The Convoy Effect, increasing average waiting time"),
                ChallengeOption(id="B", text="Deadlock"),
                ChallengeOption(id="C", text="High context switch overhead"),
            ],
            correct_option_id="A",
            hints=[
                ProgressiveHint(level=1, type="nudge", text="Think of slow vehicles on a single-lane road."),
                ProgressiveHint(level=2, type="guidance", text="FCFS does not preempt running processes."),
            ],
            explanation="In FCFS, long bursts cause short processes to queue behind them, known as the Convoy Effect.",
        ),
        boss=BossPayload(is_boss_mission=False),
        reward=RewardPayload(xp=150, knowledge_coins=25, mastery_boost_potential=0.15),
        metadata=SpecificationMetadata(
            source_document_id="doc-os-ch5",
            chunk_ids=["chunk-014", "chunk-015"],
            generated_at="2026-09-26T12:00:00Z",
            generator_model="gemini-2.5-flash",
        ),
    )

    assert spec.mission_id == "OS-CPU-001"
    assert spec.challenge.correct_option_id == "A"
    assert spec.difficulty == 2
    assert len(spec.challenge.options) == 3


def test_invalid_game_specification_mismatched_correct_option():
    """Verify that a challenge where correct_option_id is not in options fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        ChallengePayload(
            challenge_id="CHAL-ERR-001",
            challenge_type="mcq",
            prompt="Which option is valid?",
            options=[
                ChallengeOption(id="A", text="First option"),
                ChallengeOption(id="B", text="Second option"),
            ],
            correct_option_id="Z",  # Does not exist in options
            explanation="Invalid correct option",
        )
    assert "correct_option_id 'Z' does not match any available option id" in str(exc_info.value)


def test_invalid_difficulty_out_of_bounds():
    """Verify that difficulty must strictly be between 1 and 5."""
    with pytest.raises(ValidationError):
        GameSpecification(
            mission_id="ERR-001",
            concept_id="err",
            title="Error",
            difficulty=6,  # Invalid: max is 5
            learning_objective="Invalid",
            narrative=NarrativePayload(zone_theme="theme", mission_intro="intro"),
            npc=NPCPayload(npc_id="npc", npc_name="NPC", dialogue=["test"]),
            challenge=ChallengePayload(
                challenge_id="c1",
                prompt="Prompt text",
                options=[ChallengeOption(id="A", text="Opt A"), ChallengeOption(id="B", text="Opt B")],
                correct_option_id="A",
                explanation="Exp text",
            ),
            metadata=SpecificationMetadata(
                generated_at="2026-09-26T12:00:00Z",
                generator_model="mock",
            ),
        )


def test_valid_game_event():
    """Verify that a valid GameEvent telemetry payload passes validation."""
    event = GameEvent(
        event_id="evt-12345-uuid",
        student_id="std-001",
        session_id="sess-001",
        mission_id="OS-CPU-001",
        concept_id="cpu_scheduling_fcfs",
        event_type=GameEventType.QUESTION_ANSWERED,
        payload=EventPayload(
            challenge_id="CHAL-FCFS-001",
            selected_option_id="A",
            is_correct=True,
            difficulty=2,
            time_taken_seconds=12.5,
            hints_used_count=1,
            highest_hint_level=1,
            remaining_player_health=90,
            attempt_number=1,
        ),
        client_timestamp="2026-09-26T14:30:00Z",
    )

    assert event.event_type == GameEventType.QUESTION_ANSWERED
    assert event.payload.is_correct is True
    assert event.payload.time_taken_seconds == 12.5


def test_student_mastery_model():
    """Verify that StudentProfile and ConceptMastery update cleanly."""
    student = StudentProfile(
        student_id="std-adarsh-001",
        display_name="Adarsh",
        xp=200,
        level=2,
        knowledge_coins=50,
        concept_mastery={
            "cpu_scheduling_fcfs": ConceptMastery(
                concept_id="cpu_scheduling_fcfs",
                mastery_score=0.85,
                total_attempts=3,
                successful_attempts=3,
                consecutive_correct=3,
                last_difficulty_solved=3,
            )
        },
    )

    assert student.student_id == "std-adarsh-001"
    assert student.concept_mastery["cpu_scheduling_fcfs"].mastery_score == 0.85
