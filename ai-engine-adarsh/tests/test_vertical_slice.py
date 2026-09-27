"""End-to-end vertical slice demonstration of the complete ARCANA-AI Brain lifecycle."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from shared.schemas.game_specification import GameSpecification
from shared.schemas.game_event import GameEvent, GameEventType, EventPayload

client = TestClient(app)

CPU_SCHEDULING_CORPUS = """
Chapter 5: CPU Scheduling

5.1 Basic Concepts
CPU scheduling is the basis of multi-programmed operating systems. By switching the CPU among processes, the operating system can make the computer more productive. In a uniprocessor system, only one process can run at a time; any others must wait until the CPU is free and can be rescheduled.

5.2 First-Come, First-Served (FCFS) Scheduling
By far the simplest CPU-scheduling algorithm is the first-come, first-served (FCFS) algorithm. With this scheme, the process that requests the CPU first is allocated the CPU first. The implementation of the FCFS policy is easily managed with a FIFO queue. When a process enters the ready queue, its PCB is linked onto the tail of the queue. However, the average waiting time under the FCFS policy is often quite long, especially if a long process arrives first, causing the convoy effect.

5.3 Shortest-Job-First (SJF) Scheduling
A different approach to CPU scheduling is the shortest-job-first (SJF) algorithm. This algorithm associates with each process the length of the process's next CPU burst. When the CPU is available, it is assigned to the process that has the smallest next CPU burst. The SJF scheduling algorithm is provably optimal, in that it gives the minimum average waiting time for a given set of processes. The real difficulty with the SJF algorithm is knowing the length of the next CPU request.

5.4 Round-Robin (RR) Scheduling
The round-robin (RR) scheduling algorithm is designed especially for timesharing systems. It is similar to FCFS scheduling, but preemption is added to enable the system to switch between processes. A small unit of time, called a time quantum or time slice, is defined. A time quantum is generally from 10 to 100 milliseconds in length. The ready queue is treated as a circular queue. If the time quantum is too large, RR degenerates into FCFS. If it is too small, context-switch overhead dominates.
"""


def test_complete_vertical_slice_lifecycle():
    """Demonstrates complete end-to-end integration:

    1. Ingestion -> 2. Chunking -> 3. Knowledge Graph -> 4. Student Setup ->
    5. Mission Generation -> 6. Gameplay Telemetry -> 7. Mastery Progression ->
    8. Socratic Tutor -> 9. Boss Encounter Generation.
    """
    # 1. Ingest document
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("cpu_scheduling.txt", CPU_SCHEDULING_CORPUS.encode("utf-8"), "text/plain")},
    )
    assert upload_res.status_code in (200, 202)
    doc_data = upload_res.json()
    doc_id = doc_data["document_id"]
    assert doc_id is not None

    # 2. Chunk document
    chunk_res = client.post(f"/api/v1/documents/{doc_id}/chunks")
    assert chunk_res.status_code == 200
    chunk_data = chunk_res.json()
    assert chunk_data["total_chunks"] >= 2

    # 3. Knowledge Extraction & Learning Graph
    graph_res = client.get(f"/api/v1/documents/{doc_id}/graph")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert graph_data["total_nodes"] >= 2
    concepts = graph_data["nodes"]
    first_concept_id = concepts[0]["concept_id"]

    # 4. Student Registration
    student_id = "cadet_alex_99"
    student_res = client.post("/api/v1/students", json={"student_id": student_id, "display_name": "Cadet Alex"})
    assert student_res.status_code == 200
    assert student_res.json()["xp"] == 0

    # 5. Adaptive Mission Sequencer -> Generate GameSpecification
    mission_res = client.post(
        "/api/v1/sequencer/next-mission",
        json={"student_id": student_id, "document_id": doc_id},
    )
    assert mission_res.status_code == 200
    game_spec = mission_res.json()
    assert game_spec["version"] == "1.0.0"
    assert "narrative" in game_spec
    assert "npc" in game_spec
    assert "challenge" in game_spec
    assert len(game_spec["challenge"]["hints"]) == 3
    correct_opt = game_spec["challenge"]["correct_option_id"]

    # 6. Simulate Gameplay Telemetry: Player correctly solves challenge
    telemetry_payload = {
        "version": "1.0.0",
        "event_id": "evt_slice_001",
        "student_id": student_id,
        "session_id": "session_game_001",
        "mission_id": game_spec["mission_id"],
        "concept_id": game_spec["concept_id"],
        "event_type": "QUESTION_ANSWERED",
        "payload": {
            "challenge_id": game_spec["challenge"]["challenge_id"],
            "selected_option_id": correct_opt,
            "is_correct": True,
            "difficulty": game_spec["difficulty"],
            "time_taken_seconds": 15.2,
            "hints_used_count": 0,
        },
        "client_timestamp": "2026-09-27T12:30:00Z",
    }
    telemetry_res = client.post("/api/v1/telemetry/events", json=telemetry_payload)
    assert telemetry_res.status_code == 200
    t_data = telemetry_res.json()
    assert t_data["mastery_updated"] is True
    assert t_data["xp_awarded"] > 0
    assert t_data["mastery_result"]["new_score"] > 0

    # 7. Student Profile reflects updated mastery & XP
    profile_res = client.get(f"/api/v1/students/{student_id}")
    assert profile_res.status_code == 200
    p_data = profile_res.json()
    assert p_data["xp"] > 0
    assert game_spec["concept_id"] in p_data["concept_mastery"]

    # 8. Socratic Tutor unsticking query
    tutor_res = client.post(
        "/api/v1/tutor/ask",
        json={
            "student_id": student_id,
            "concept_id": game_spec["concept_id"],
            "query": "How does context switching overhead affect the choice of time slice?",
            "document_id": doc_id,
        },
    )
    assert tutor_res.status_code == 200
    tutor_data = tutor_res.json()
    assert len(tutor_data["reply"]) > 20
    assert len(tutor_data["guiding_question"]) > 10

    # 9. Boss Battle Generation for curriculum milestone
    boss_res = client.post(
        "/api/v1/generation/boss",
        json={"concept_id": game_spec["concept_id"], "phases": 3},
    )
    assert boss_res.status_code == 200
    boss_data = boss_res.json()
    assert boss_data["phases"] == 3
    assert boss_data["hp"] == 300
    assert len(boss_data["challenges"]) == 3
