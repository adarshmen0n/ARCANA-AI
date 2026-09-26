# AI Engine — Adarsh 🧠

## Ownership & Domain
**Owner**: Adarsh (AI Engine / AI Brain / AI Architecture / Integration Lead)

This directory houses the intelligence layer of ARCANA-AI. The AI Engine transforms educational materials into structured knowledge, tracks student comprehension, adaptively plans curriculum, and generates gameplay specifications.

## Strict Boundaries
### The AI Engine OWNS:
- Educational content ingestion, normalization, and semantic chunking.
- Embeddings generation, vector storage, and RAG retrieval pipelines.
- Knowledge extraction (topics, concepts, prerequisites, learning graph).
- Student learner model, deterministic mastery estimation, and difficulty scaling.
- Generators: lessons, questions, progressive hints, NPC dialogues, missions, boss challenges.
- `GameSpecification` generation complying strictly with `shared/schemas/game_specification.py`.
- `GameEvent` telemetry ingestion and adaptive mastery updating.
- Provider abstractions (Gemini, local models) with fallback and circuit breaker strategies.

### The AI Engine DOES NOT OWN:
- UI rendering or mobile/web layout (owned by Jeenth & Kruthic).
- Game physics, rendering loop, sprite movement, or collisions (owned by Dasarth).
- Database infrastructure or raw user authentication (owned by Abhishek).

## Module Structure (Target Architecture)
```
ai-engine-adarsh/
├── app/
│   ├── api/v1/         # FastAPI endpoints (/documents, /experience/next, /events, /tutor)
│   ├── core/           # Configuration, logging, security, telemetry
│   └── main.py         # Application entrypoint & health checks
├── ingestion/          # Document validation, extraction (PDF, DOCX, TXT)
├── chunking/           # Semantic & structural chunking strategies
├── rag/                # Embeddings, vector retrieval, reranking, source citations
├── knowledge/          # Concept extraction, prerequisite graph builder
├── student/            # Student state, mastery scoring engine, difficulty curves
├── generation/         # Individual generators (lesson, question, hint, mission, boss)
├── game_spec/          # Transformation layer to GameSpecification
├── events/             # GameEvent processing & feedback loops
├── providers/          # LLM and embedding provider adapters (Gemini, fallback)
├── prompts/            # Centralized, versioned prompt templates
└── tests/              # Subsystem unit and integration tests
```
