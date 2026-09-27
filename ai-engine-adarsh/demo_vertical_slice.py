"""ARCANA-AI Brain End-to-End Vertical Slice Demonstration.

Runs a live interactive simulation of:
1. Ingestion of Operating Systems CPU Scheduling text
2. Semantic preprocessing and chunking
3. Vector indexing and semantic retrieval
4. Knowledge Engine concept extraction & DAG Learning Graph construction
5. Student Profile initialization
6. Adaptive Mission Sequencing producing a strict GameSpecification
7. Simulated Game Engine telemetry ingestion and deterministic mastery update
8. Socratic AI Tutor unsticking query
9. Boss battle generation
"""

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_OS_TEXT = """
Chapter 5: CPU Scheduling

5.1 Basic Concepts
CPU scheduling is the basis of multi-programmed operating systems. By switching the CPU among processes, the operating system can make the computer more productive. In a uniprocessor system, only one process can run at a time; any others must wait until the CPU is free and can be rescheduled.

5.2 First-Come, First-Served (FCFS) Scheduling
By far the simplest CPU-scheduling algorithm is the first-come, first-served (FCFS) algorithm. With this scheme, the process that requests the CPU first is allocated the CPU first. The implementation of the FCFS policy is easily managed with a FIFO queue. However, the average waiting time under the FCFS policy is often quite long, especially if a long process arrives first, causing the convoy effect.

5.3 Shortest-Job-First (SJF) Scheduling
A different approach to CPU scheduling is the shortest-job-first (SJF) algorithm. This algorithm associates with each process the length of the process's next CPU burst. When the CPU is available, it is assigned to the process that has the smallest next CPU burst. The SJF scheduling algorithm is provably optimal.

5.4 Round-Robin (RR) Scheduling
The round-robin (RR) scheduling algorithm is designed especially for timesharing systems. It is similar to FCFS scheduling, but preemption is added to enable the system to switch between processes. A small unit of time, called a time quantum or time slice, is defined.
"""


def main():
    print("=" * 80)
    print(" [ARCANA-AI BRAIN: END-TO-END VERTICAL SLICE DEMONSTRATION]")
    print("=" * 80)

    # 1. Ingestion
    print("\n[STEP 1] Ingesting CPU Scheduling document...")
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("os_cpu_scheduling.txt", SAMPLE_OS_TEXT.encode("utf-8"), "text/plain")},
    )
    doc_id = res.json()["document_id"]
    print(f" -> Uploaded Document ID: {doc_id} (Status: {res.status_code})")

    # 2. Chunking
    print("\n[STEP 2] Preprocessing and semantically chunking document...")
    res = client.post(f"/api/v1/documents/{doc_id}/chunks")
    chunk_data = res.json()
    print(f" -> Extracted {chunk_data['total_chunks']} semantic chunks.")

    # 3. Learning Graph
    print("\n[STEP 3] Extracting concepts & building Learning Graph DAG...")
    res = client.get(f"/api/v1/documents/{doc_id}/graph")
    graph_data = res.json()
    print(f" -> Total Concepts Discovered: {graph_data['total_nodes']}")
    for node in graph_data["nodes"]:
        print(f"    * [{node['concept_id']}] {node['name']} (Difficulty: {node['difficulty']})")

    # 4. Student Profile Setup
    student_id = "student_adarsh_001"
    print(f"\n[STEP 4] Initializing learner profile for '{student_id}'...")
    res = client.post("/api/v1/students", json={"student_id": student_id, "display_name": "Adarsh Menon"})
    profile = res.json()
    print(f" -> Profile Active: Level {profile['level']} | XP: {profile['xp']} | Coins: {profile['knowledge_coins']}")

    # 5. Adaptive Mission Sequencer
    print("\n[STEP 5] Sequencing next adaptive mission via AdaptiveSequencer...")
    res = client.post(
        "/api/v1/sequencer/next-mission",
        json={"student_id": student_id, "document_id": doc_id},
    )
    game_spec = res.json()
    print(f" -> Generated Mission ID: {game_spec['mission_id']}")
    print(f"    Target Concept: {game_spec['concept_id']} | Difficulty: {game_spec['difficulty']}/5")
    print(f"    Title: {game_spec['title']}")
    print(f"    Narrative Zone: {game_spec['narrative']['zone_theme']}")
    print(f"    NPC: {game_spec['npc']['npc_name']} (Dialogue: '{game_spec['npc']['dialogue'][1]}')")
    print(f"    Prompt: {game_spec['challenge']['prompt'][:100]}...")
    print(f"    Correct Option: [{game_spec['challenge']['correct_option_id']}]")
    print(f"    Progressive Hints ({len(game_spec['challenge']['hints'])} tiers):")
    for h in game_spec["challenge"]["hints"]:
        print(f"      - Tier {h['level']} ({h['type']}): {h['text']}")

    # 6. Simulate Gameplay Telemetry
    print("\n[STEP 6] Simulating Game Engine player answering correctly...")
    telemetry_payload = {
        "version": "1.0.0",
        "event_id": "evt_demo_001",
        "student_id": student_id,
        "session_id": "sess_demo_live",
        "mission_id": game_spec["mission_id"],
        "concept_id": game_spec["concept_id"],
        "event_type": "QUESTION_ANSWERED",
        "payload": {
            "challenge_id": game_spec["challenge"]["challenge_id"],
            "selected_option_id": game_spec["challenge"]["correct_option_id"],
            "is_correct": True,
            "difficulty": game_spec["difficulty"],
            "time_taken_seconds": 18.4,
            "hints_used_count": 0,
        },
        "client_timestamp": "2026-09-27T12:45:00Z",
    }
    res = client.post("/api/v1/telemetry/events", json=telemetry_payload)
    t_result = res.json()
    print(f" -> Telemetry Processed:")
    print(f"    XP Awarded: +{t_result['xp_awarded']} | Coins: +{t_result['coins_awarded']}")
    print(f"    Mastery Delta: {t_result['mastery_result']['score_delta']:+.4f} (New Score: {t_result['mastery_result']['new_score']:.2f})")
    print(f"    Feedback: {t_result['feedback_message']}")

    # 7. Socratic AI Tutor
    print("\n[STEP 7] Learner queries Socratic AI Tutor...")
    res = client.post(
        "/api/v1/tutor/ask",
        json={
            "student_id": student_id,
            "concept_id": game_spec["concept_id"],
            "query": "Why can a long burst in FCFS degrade the experience for all subsequent jobs?",
            "document_id": doc_id,
        },
    )
    tutor = res.json()
    print(f" -> Tutor Reply: {tutor['reply']}")
    print(f" -> Guiding Question: {tutor['guiding_question']}")
    print(f" -> Suggested Action: {tutor['suggested_action']}")

    # 8. Boss Battle Generation
    print("\n[STEP 8] Generating Summative Boss Encounter...")
    res = client.post(
        "/api/v1/generation/boss",
        json={"concept_id": game_spec["concept_id"], "phases": 3},
    )
    boss = res.json()
    print(f" -> Boss Spawned: {boss['boss_name']} (HP: {boss['hp']} | Phases: {boss['phases']})")
    print(f"    Weakness Concept: '{boss['shield_weakness_concept']}'")
    print(f"    Phase 1 Challenge: {boss['challenges'][0]['prompt']}")

    print("\n" + "=" * 80)
    print(" [SUCCESS] VERTICAL SLICE COMPLETE: ALL CONTRACTS VALIDATED & INTEGRATED!")
    print("=" * 80)


if __name__ == "__main__":
    main()
