# ARCANA AI Brain — Team Integration Guide & API Specification

**Subsystem**: ARCANA AI Brain Engine  
**Lead Architect**: Adarsh Menon (`ai-engine/`)  
**Contract Version**: `1.0`  
**API Prefix**: `/api/v1`  
**Base URL (Local)**: `http://localhost:8000`  

---

## 1. Executive Overview

The ARCANA AI Brain is the cognitive orchestration engine of the ARCANA platform. It converts raw educational materials (PDF, DOCX, PPTX, TXT, MD) into structured, game-engine-ready educational specifications conforming to **Contract v1.0**.

This document outlines the exact integration contracts for each teammate:
- **Section 2**: Integration Guide for **Dasarth** (Game Systems Engineer)
- **Section 3**: Integration Guide for **Abhishek & Jeenath** (Frontend & Backend UI Engineers)
- **Section 4**: Integration Guide for **Kruthic** (Mobile UI/UX & Visual Experience Designer)

---

## 2. Guide for Dasarth (Game Systems Engineer)

### 2.1 The Contract Boundary
Your game systems engine (Godot / Unity / WebGL / Custom Engine) interfaces with the AI Engine via **Game Specification Contract v1.0** (`schemas/game_spec.py`).

The specification is pure JSON data. Your engine **never executes arbitrary code**; it maps predefined game mechanics and entities to data objects.

### 2.2 Contract Schema Structure
```json
{
  "schema_version": "1.0",
  "campaign": {
    "id": "cmp_9dedba564ef9",
    "title": "The Raft & Byzantine Chronicles",
    "subject": "Distributed Consensus",
    "difficulty": 2,
    "chapters": [
      {
        "id": "chp_59b5d7a5d99f",
        "title": "Chapter 1: 1. The Distributed Consensus Problem & Foundations",
        "description": "Mastery of 3 core concepts.",
        "missions": [
          {
            "mission_id": "msn_c0f82521a5f0",
            "title": "Trial of 1. The Distributed Consensus Problem",
            "concept_ids": ["cpt_46e6a2dede0f"],
            "learning_objective": "Analyze and evaluate...",
            "mechanic": "quiz",
            "challenge": {
              "mechanic_type": "quiz",
              "target_concept": "1. The Distributed Consensus Problem",
              "time_limit_seconds": 120
            },
            "difficulty": 3,
            "story": {
              "world": "Arcana Realm Citadel",
              "context": "The archive sector has experienced drift...",
              "motivation": "Mastering this concept stabilizes the node.",
              "mission_setting": "Archive Vault"
            },
            "npc": {
              "npc_id": "npc_67d10c17e98d",
              "name": "Archivist of Distributed Consensus",
              "role": "Educational Mentor",
              "tone": "encouraging",
              "dialogue": ["Greetings, seeker...", "Pay careful attention..."]
            },
            "questions": [
              {
                "question_id": "qst_c95c30a752cc",
                "type": "mcq",
                "question": "What is the primary role...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "Because...",
                "difficulty": 3
              }
            ],
            "hints": [
              {"hint_id": "hnt_1", "tier": 1, "text": "Reminder..."},
              {"hint_id": "hnt_2", "tier": 2, "text": "Directional clue..."},
              {"hint_id": "hnt_3", "tier": 3, "text": "Strong hint..."},
              {"hint_id": "hnt_4", "tier": 4, "text": "Near-answer guidance..."}
            ],
            "rewards": {
              "xp": 100,
              "currency": 25,
              "badges": ["Consensus Novice"]
            }
          }
        ],
        "boss": {
          "challenge_id": "bss_1",
          "title": "Guardian of Consensus",
          "required_score": 0.85
        }
      }
    ]
  }
}
```

### 2.3 Supported Mechanics Enum (`GameMechanic`)
1. `quiz`: Multi-choice or scenario questions.
2. `matching`: Connect concept terms to definitions.
3. `ordering`: Kahn's DAG dependency or algorithmic ordering.
4. `puzzle`: Logical rule completion.
5. `exploration`: Interactive world discovery.
6. `boss_fight`: Comprehensive multi-stage mastery challenge.

---

## 3. Guide for Abhishek & Jeenath (Frontend / Backend)

### 3.1 REST API Overview
The AI Engine runs on FastAPI and exposes REST endpoints under `/api/v1`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/documents/process-text` | Submit raw text or markdown for compilation. |
| `POST` | `/api/v1/documents/upload` | Upload `.pdf`, `.docx`, `.pptx`, `.txt`, `.md` file. |
| `GET` | `/api/v1/jobs/{job_id}` | Poll or check background job progress. |
| `POST` | `/api/v1/tutor/message` | Socratic AI Tutor multi-turn dialogue. |
| `POST` | `/api/v1/rag/query` | RAG grounded retrieval query with chunk citations. |
| `POST` | `/api/v1/analytics/events` | Ingest player telemetry for EMA learner mastery calculation. |

### 3.2 Key Request & Response Examples

#### A. Ingest Document Synchronously
```http
POST /api/v1/documents/process-text HTTP/1.1
Content-Type: application/json

{
  "text": "# Operating Systems\n## Semaphores\nSemaphores regulate access...",
  "filename": "os.txt",
  "subject": "Operating Systems",
  "async_mode": false
}
```
**Response (200 OK)**:
Returns full `PipelineResult` with `document`, `chunks`, `knowledge_graph`, `learning_graph`, `game_specification`, and `timings_ms`.

#### B. Socratic AI Tutor
```http
POST /api/v1/tutor/message HTTP/1.1
Content-Type: application/json

{
  "user_id": "usr_adarsh",
  "message": "I don't understand how semaphores prevent deadlocks.",
  "concept_id": "cpt_semaphores",
  "history": []
}
```
**Response (200 OK)**:
```json
{
  "response": "Think of a semaphore as a key to a room. If there is only one key...",
  "suggested_questions": ["What happens if two processes request the key simultaneously?"],
  "pedagogical_intent": "scaffold_understanding"
}
```

#### C. Player Analytics & EMA Mastery
```http
POST /api/v1/analytics/events HTTP/1.1
Content-Type: application/json

{
  "user_id": "usr_adarsh",
  "events": [
    {
      "event_type": "question_answered",
      "concept_id": "cpt_semaphores",
      "success": true,
      "response_time_ms": 4200
    }
  ]
}
```
The AI Engine recalculates the learner's mastery using Exponential Moving Average:
$$M_t = \alpha \cdot S_t + (1 - \alpha) \cdot M_{t-1}$$
with $\alpha = 0.3$. If $M_t < 0.4$, adaptive revision missions are automatically triggered.

---

## 4. Guide for Kruthic (Mobile UI / UX & Animation)

### 4.1 Narrative & World Scaffolding
- Every mission includes a `story` object with `world`, `context`, `motivation`, and `mission_setting`.
- Use the `mission_setting` (e.g. *"Archive Vault"*, *"Citadel Core"*) to load corresponding 3D/2D background environments, ambient lighting, and particle effects.

### 4.2 Progressive 4-Tier Hints
When a player struggles, trigger hints sequentially:
- **Tier 1 (Reminder)**: Gentle recap of the core principle.
- **Tier 2 (Directional)**: Guidance on where in the problem to focus.
- **Tier 3 (Strong Clue)**: Deep conceptual hint eliminating false options.
- **Tier 4 (Near-Answer)**: Final step scaffolding right before the solution.

### 4.3 NPCs & Emotional Tone
Each NPC defines an explicit `tone`:
- `encouraging`: Warm mentor expressions and bright aura.
- `analytical`: Precise, logical HUD data overlays.
- `mysterious`: Shadowed framing and cryptic ancient lore.
- `challenging`: Dynamic boss battle stance.

---

## 5. Development & Deployment

### Run Locally:
```bash
cd ai-engine
uvicorn app.main:app --reload --port 8000
```
Interactive OpenAPI documentation will be live at `http://localhost:8000/docs`.

### Run Unit Tests:
```bash
pytest tests/ -v  # 46 passed in 1.88s
```
