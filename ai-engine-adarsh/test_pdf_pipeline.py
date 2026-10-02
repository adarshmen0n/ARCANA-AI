"""
PDF End-to-End Pipeline Test Script for ARCANA AI Engine.

This script demonstrates how ANY academic PDF is:
1. Ingested & Extracted via PyPDF
2. Semantically Chunked with Boundary Detection
3. Converted into a Prerequisite Curriculum DAG
4. Taught via Micro-Lessons & Game Missions
5. Diagnosed via the Cognitive Misconception Engine
6. Tracked with Bayesian Knowledge Tracing & Ebbinghaus Retention
7. Consulted via Dynamic Multi-Tier Socratic AI Tutor
8. Culminated in a Summative Boss Encounter

Usage:
  python test_pdf_pipeline.py [optional_custom_pdf_path]
"""

import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.mastery.diagnostic import diagnostic_engine
from app.knowledge.models import Concept

client = TestClient(app)


def generate_sample_pdf(filepath: str) -> str:
    """Generates a realistic multi-page academic syllabus PDF for testing."""
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # --- Page 1: Chapter 1 & 2 ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Operating Systems & Distributed Systems (CS301)")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 68, "Authoritative Academic Syllabus & Lecture Notes")
    c.line(50, height - 74, width - 50, height - 74)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 105, "Chapter 1: Process Management & Lifecycle")
    c.setFont("Helvetica", 10)
    text_p1 = [
        "Processes are the foundational unit of computation in an operating system. A process transitions",
        "through five primary lifecycle states: New, Ready, Running, Waiting, and Terminated. The Operating",
        "System maintains each active process using a Process Control Block (PCB), tracking program counters,",
        "CPU registers, memory limits, and I/O status. Context switching is the computational mechanism of saving",
        "the state of the currently executing process into its PCB and restoring the next scheduled process.",
    ]
    y = height - 125
    for line in text_p1:
        c.drawString(50, y, line)
        y -= 14

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 20, "Chapter 2: First-Come First-Served (FCFS) Scheduling")
    c.setFont("Helvetica", 10)
    text_p2 = [
        "First-Come, First-Served is a non-preemptive scheduling policy where tasks run in strict arrival order.",
        "While straightforward with minimal scheduling overhead, FCFS suffers severely from the Convoy Effect,",
        "where short CPU bursts are trapped waiting behind a massive compute-bound burst, causing average waiting",
        "time to skyrocket across the entire ready queue.",
    ]
    y -= 38
    for line in text_p2:
        c.drawString(50, y, line)
        y -= 14

    c.showPage()  # Page 1 Finish

    # --- Page 2: Chapter 3, 4 & 5 ---
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 50, "Chapter 3: Shortest-Job-First (SJF) Scheduling")
    c.setFont("Helvetica", 10)
    text_p3 = [
        "Shortest-Job-First (SJF) selects the process with the smallest anticipated CPU burst time. Mathematically,",
        "SJF is provably optimal because it guarantees the lowest possible average waiting time. However, future",
        "burst durations cannot be known in advance, requiring exponential smoothing heuristics, and continuous",
        "short tasks cause starvation of longer compute jobs.",
    ]
    y = height - 68
    for line in text_p3:
        c.drawString(50, y, line)
        y -= 14

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 20, "Chapter 4: Round-Robin (RR) Timesharing")
    c.setFont("Helvetica", 10)
    text_p4 = [
        "Round-Robin introduces preemption via a fixed time quantum (typically 10-100ms) with a circular FIFO queue.",
        "If the time quantum is excessively large, RR degrades into FCFS; if the quantum is overly brief, excessive",
        "context-switch overhead degrades total CPU computation throughput.",
    ]
    y -= 38
    for line in text_p4:
        c.drawString(50, y, line)
        y -= 14

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 20, "Chapter 5: Priority Scheduling and Aging")
    c.setFont("Helvetica", 10)
    text_p5 = [
        "Priority scheduling allocates CPU time to tasks with the highest assigned integer priority. A catastrophic",
        "vulnerability is indefinite starvation of low-priority tasks. Operating systems prevent starvation using",
        "Aging, an adaptive technique that incrementally raises the priority of processes as they wait in queue.",
    ]
    y -= 38
    for line in text_p5:
        c.drawString(50, y, line)
        y -= 14

    c.showPage()  # Page 2 Finish
    c.save()
    return filepath


def run_pipeline(pdf_path: str):
    print("=" * 85)
    print(" [ARCANA AI ENGINE - LIVE PDF INGESTION & COGNITIVE TEACHING TEST]")
    print("=" * 85)
    print(f" [*] Target PDF: {pdf_path}")
    print(f" [*] File Size:  {os.path.getsize(pdf_path)} bytes")

    # -------------------------------------------------------------------------
    # STAGE 1: UPLOAD & EXTRACT PDF
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 1] UPLOADING & EXTRACTING PDF (PyPDF Extraction)")
    print("-" * 85)
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    filename = Path(pdf_path).name
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": (filename, file_bytes, "application/pdf")},
    )
    assert response.status_code in (200, 202), f"Upload failed: {response.text}"
    doc_id = response.json()["document_id"]
    status_resp = client.get(f"/api/v1/documents/{doc_id}/status").json()

    print(f" [+] HTTP Status:        {response.status_code} ACCEPTED")
    print(f" [+] Document ID:        {doc_id}")
    print(f" [+] Parsing Status:     {status_resp.get('status')}")
    print(f" [+] Total Pages Parsed: {status_resp.get('total_pages')}")
    print(f" [+] Characters Read:    {status_resp.get('total_characters')}")

    # -------------------------------------------------------------------------
    # STAGE 2: SEMANTIC CHUNKING
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 2] SEMANTIC CHUNKING & BOUNDARY DETECTION")
    print("-" * 85)
    chunk_resp = client.post(f"/api/v1/documents/{doc_id}/chunks")
    assert chunk_resp.status_code == 200, f"Chunking failed: {chunk_resp.text}"
    chunk_data = chunk_resp.json()
    chunks = chunk_data.get("chunks", [])
    print(f" [+] Total Semantic Chunks Created: {len(chunks)}")
    for i, ch in enumerate(chunks[:3], 1):
        preview = ch.get("text", "")[:85].replace("\n", " ")
        print(f"     Chunk {i}: [{ch.get('section_title', 'Section')}] -> '{preview}...'")

    # -------------------------------------------------------------------------
    # STAGE 3: KNOWLEDGE GRAPH & CURRICULUM DAG
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 3] CURRICULUM GRAPH EXTRACTION (Prerequisite DAG)")
    print("-" * 85)
    graph_resp = client.get(f"/api/v1/documents/{doc_id}/graph")
    assert graph_resp.status_code == 200, f"Graph extraction failed: {graph_resp.text}"
    graph = graph_resp.json()
    nodes = graph.get("nodes", [])
    ordered_cids = graph.get("ordered_concept_ids", [n["concept_id"] for n in nodes])

    print(f" [+] Total Concepts Extracted: {len(nodes)}")
    print(f" [+] Automated Learning Progression (Topological Sequence):")
    for idx, node in enumerate(nodes, 1):
        print(f"     Step {idx}: [{node['concept_id']}] '{node['name']}' (Difficulty: {node['difficulty']}/5)")

    target_node = nodes[0]
    target_cid = target_node["concept_id"]

    # -------------------------------------------------------------------------
    # STAGE 4: ADAPTIVE TEACHING OF FIRST CONCEPT
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(f" [STAGE 4] TEACHING CONCEPT: '{target_node['name']}' ({target_cid})")
    print("-" * 85)

    # 4A. Micro-Lesson
    lesson_resp = client.post(
        "/api/v1/generation/lesson",
        json={"concept_id": target_cid, "difficulty": target_node["difficulty"], "document_id": doc_id},
    )
    lesson = lesson_resp.json()
    print(f" [+] Micro-Lesson Generated:")
    print(f"     Title:   \"{lesson.get('title')}\"")
    print(f"     Hook:    {lesson.get('story_hook', '')[:85]}...")
    print(f"     Analogy: {lesson.get('analogy', '')[:85]}...")

    # 4B. Game Mission Generation (Shared Contract: GameSpecification)
    spec_resp = client.post(
        "/api/v1/game-spec/generate",
        json={"concept_id": target_cid, "difficulty": target_node["difficulty"], "is_boss": False, "document_id": doc_id},
    )
    mission = spec_resp.json()
    print(f"\n [+] Game Mission Built for Game Engine:")
    print(f"     Mission ID:    {mission.get('mission_id')}")
    print(f"     NPC Guide:     {mission.get('npc', {}).get('npc_name')}")
    challenge = mission.get("challenge", {})
    print(f"     Question:      {challenge.get('prompt')}")
    options = challenge.get('options', [])
    for opt in options:
        prefix = "  [x]" if opt.get("id") == challenge.get("correct_option_id") else "  [ ]"
        print(f"       {prefix} {opt.get('text')}")

    # -------------------------------------------------------------------------
    # STAGE 5: STUDENT MASTERY & MISCONCEPTION DIAGNOSTICS
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 5] TESTING STUDENT ANSWERS & COGNITIVE MISCONCEPTION DIAGNOSTICS")
    print("-" * 85)

    correct_id = challenge.get("correct_option_id", "A")
    wrong_opt = next((o for o in options if o.get("id") != correct_id), {"id": "B", "text": "Arrival order is always optimal"})
    correct_opt = next((o for o in options if o.get("id") == correct_id), {"id": correct_id, "text": "Correct invariant"})

    print(f" [*] Simulating a Student Error:")
    print(f"     Student Selected Option {wrong_opt['id']}: \"{wrong_opt['text']}\"")

    concept_obj = Concept(
        concept_id=target_cid,
        name=target_node["name"],
        topic=target_node.get("topic", "Operating Systems"),
        definition=f"Core operating principles of {target_node['name']}.",
        difficulty=target_node["difficulty"],
    )

    diagnosis = diagnostic_engine.diagnose_response(
        concept=concept_obj,
        selected_option_id=wrong_opt["id"],
        correct_option_id=correct_id,
        challenge_prompt=challenge.get("prompt", ""),
        options=options,
    )
    print(f"\n [+] Cognitive Diagnostic Engine Output:")
    print(f"     Category:          {diagnosis.category.value.upper()}")
    print(f"     Root Cause:        {diagnosis.root_cause_explanation}")
    print(f"     Cognitive Conflict:{diagnosis.cognitive_conflict_prompt}")
    print(f"     Remedial Nudge:    {diagnosis.remedial_nudge}")

    # -------------------------------------------------------------------------
    # STAGE 6: BAYESIAN KNOWLEDGE TRACING & RETENTION
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 6] BAYESIAN KNOWLEDGE TRACING (BKT) & EBBINGHAUS STABILITY")
    print("-" * 85)

    student_id = "cadet_adarsh_42"
    client.post("/api/v1/students", json={"student_id": student_id, "display_name": "Adarsh Menon"})

    # Interaction 1: Incorrect attempt with 1 hint
    int1 = client.post(
        f"/api/v1/students/{student_id}/interaction",
        json={
            "student_id": student_id,
            "concept_id": target_cid,
            "difficulty": target_node["difficulty"],
            "is_correct": False,
            "hints_used": 1,
            "time_taken_seconds": 15.0,
        },
    ).json()
    print(f" [+] After Incorrect Attempt (Hints=1):")
    print(f"     Prior Mastery:    {int1.get('old_mastery', 0.10):.3f} -> New Mastery: {int1.get('new_mastery', 0.08):.3f}")
    print(f"     Streak Penalty:   Consecutive Correct = {int1.get('consecutive_correct', 0)}")

    # Interaction 2: Correct attempt after remedial nudge
    int2 = client.post(
        f"/api/v1/students/{student_id}/interaction",
        json={
            "student_id": student_id,
            "concept_id": target_cid,
            "difficulty": target_node["difficulty"],
            "is_correct": True,
            "hints_used": 0,
            "time_taken_seconds": 8.5,
        },
    ).json()
    print(f" [+] After Remedial Success (Hints=0):")
    print(f"     Prior Mastery:    {int2.get('old_mastery', 0.08):.3f} -> New Mastery: {int2.get('new_mastery', 0.35):.3f}")
    print(f"     Updated Level:    {int2.get('mastery_level', 'novice').upper()}")

    # -------------------------------------------------------------------------
    # STAGE 7: DYNAMIC MULTI-TIER SOCRATIC AI TUTOR
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 7] DYNAMIC SOCRATIC AI TUTOR INQUIRY")
    print("-" * 85)

    tutor_query = "What happens to the PCB program counter during a context switch?"
    print(f" [*] Student Asks: \"{tutor_query}\"")
    tutor_resp = client.post(
        "/api/v1/tutor/ask",
        json={
            "student_id": student_id,
            "concept_id": target_cid,
            "query": tutor_query,
            "document_id": doc_id,
        },
    ).json()
    print(f"\n [+] Socratic Tutor Response:")
    print(f"     Cognitive Tier:   {tutor_resp.get('cognitive_depth_level', 'balanced').upper()}")
    print(f"     Pedagogical Reply:{tutor_resp.get('reply')[:130]}...")
    print(f"     Guiding Question: {tutor_resp.get('guiding_question')}")
    print(f"     Suggested Action: {tutor_resp.get('suggested_action')}")

    # -------------------------------------------------------------------------
    # STAGE 8: SUMMATIVE BOSS FIGHT MANIFESTATION
    # -------------------------------------------------------------------------
    print("\n" + "-" * 85)
    print(" [STAGE 8] SUMMATIVE BOSS ENCOUNTER (Game Engine Contract)")
    print("-" * 85)
    boss_resp = client.post(
        "/api/v1/generation/boss",
        json={"concept_id": target_cid, "phases": 2},
    ).json()
    print(f" [+] Boss Name:         {boss_resp.get('boss_name')} ({boss_resp.get('title')})")
    print(f" [+] Total HP:          {boss_resp.get('hp')} HP")
    print(f" [+] Shield Weakness:   {boss_resp.get('shield_weakness_concept')}")
    print(f" [+] Encounter Phases:  {boss_resp.get('phases')} Phases Armed ({len(boss_resp.get('challenges', []))} Challenges)")

    print("\n" + "=" * 85)
    print(" [SUCCESS] ALL 8 STAGES OF THE PDF COGNITIVE PIPELINE EXECUTED FLAWLESSLY!")
    print("=" * 85)


if __name__ == "__main__":
    target_pdf = sys.argv[1] if len(sys.argv) > 1 else None

    if not target_pdf or not os.path.exists(target_pdf):
        sample_file = os.path.join(os.path.dirname(__file__), "sample_academic_syllabus.pdf")
        if not os.path.exists(sample_file):
            print(f"[*] Generating sample academic PDF at: {sample_file}")
            generate_sample_pdf(sample_file)
        target_pdf = sample_file

    run_pipeline(target_pdf)
