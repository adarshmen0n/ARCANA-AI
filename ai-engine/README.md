# ARCANA AI Brain (AI Engine)

> **The Educational Intelligence & Game Specification Engine for ARCANA AI**  
> *Architect & Lead: Adarsh Menon*

---

## 1. Overview & Vision

ARCANA AI transforms educational material into structured, personalized, game-ready adventures. The AI Brain is responsible for:
- **Understanding**: Ingesting educational documents, extracting concepts, semantic relationships, and maintaining grounded vector retrieval (RAG).
- **Reasoning**: Constructing the Learning Graph (DAG), computing topological learning sequences, calculating content/learner difficulty, and defining learning objectives.
- **Generating**: Producing grounded lessons, multi-type questions, progressive hints, NPC dialogues, story context, game missions, boss challenges, and rewards.
- **Personalizing**: Ingesting gameplay analytics, updating concept-level mastery models, identifying student weaknesses, and adapting subsequent learning paths.
- **Game Specification**: Exporting strictly validated, schema-compliant JSON specifications that Dasarth's Game Engine executes without arbitrary code execution.

---

## 2. Strict Boundary Model

| Component | Owner | Responsibility | What it does NOT do |
|---|---|---|---|
| **AI Brain** | **Adarsh Menon** | Knowledge extraction, reasoning, educational content, game specs, personalization | Game physics/rendering, DB persistence, UI styling |
| **Backend** | Abhishek & Jeenath | Database, Auth, file storage, API routing | AI reasoning, prompt design, learning graph logic |
| **Game Engine**| Dasarth | Godot game execution, mechanics rendering, player controls | Educational fact checking, concept extraction |
| **Mobile / UI**| Kruthick | Flutter UI, animations, client navigation | Direct LLM calls, educational rules |

---

## 3. Getting Started

### Prerequisites
- Python 3.12+ (verified on 3.12.10)
- Virtual environment or direct installation

### Installation
```bash
cd ai-engine
pip install -r requirements.txt
cp .env.example .env
```

### Running Locally
```bash
# Run FastAPI server with Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Tests
```bash
pytest -v tests/
```

---

## 4. API Endpoints (Milestone 1)

- `GET /` — Service identification and status check.
  ```json
  {
    "project": "ARCANA AI Engine",
    "status": "online",
    "version": "0.1.0"
  }
  ```
- `GET /health` — Liveness health check with environment metadata.
