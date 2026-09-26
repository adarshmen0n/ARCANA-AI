# Shared Contract: Game Engine ➔ AI Engine (`game-ai.md`)

**Contract Version**: `v1.0.0`  
**Producers**: Game Engine (Dasarth)  
**Consumers**: AI Engine (Adarsh), Backend (Abhishek)  
**Schema Implementation**: [`shared/schemas/game_event.py`](../schemas/game_event.py)  
**Type Definitions**: [`shared/types/contracts.d.ts`](../types/contracts.d.ts)

---

## 1. Overview
The Game Engine sends real-time `GameEvent` telemetry to the AI Engine as learners interact with missions, challenges, NPCs, and bosses. The AI Engine consumes these events to calculate mastery updates and dynamically adjust future learning trajectories.

---

## 2. Event Types Enum

| Event Type | Description | Trigger Moment |
| :--- | :--- | :--- |
| `QUESTION_STARTED` | Player opens/engages a question prompt. | Challenge UI activated. |
| `QUESTION_ANSWERED` | Player submits an answer choice. | Choice submitted. |
| `HINT_REQUESTED` | Player unlocks or views a hint level. | Hint button pressed. |
| `MISSION_STARTED` | Player enters a mission zone. | Level/mission loaded. |
| `MISSION_COMPLETED` | Player successfully finishes all objectives. | Victory screen rendered. |
| `MISSION_FAILED` | Player runs out of health or abandons mission. | Defeat screen rendered. |
| `NPC_INTERACTION` | Player initiates or finishes NPC dialogue. | Dialogue box stepped through. |
| `BOSS_STARTED` | Boss combat encounter begins. | Boss arena locked. |
| `BOSS_COMPLETED` | Boss is defeated via override or challenge. | Boss defeated. |
| `PLAYER_DIED` | Player health reaches zero during challenge/level. | Respawn triggered. |

---

## 3. Telemetry Event Schema

```json
{
  "$schema": "https://arcana-ai.org/schemas/v1/game-event.json",
  "version": "1.0.0",
  "event_id": "string (UUID v4)",
  "student_id": "string (UUID of learner)",
  "session_id": "string (UUID of game session)",
  "mission_id": "string (e.g. OS-CPU-001)",
  "concept_id": "string (e.g. cpu_scheduling_fcfs)",
  "event_type": "string (Enum from table above)",
  "payload": {
    "challenge_id": "string | null",
    "selected_option_id": "string | null (e.g. 'A', 'B')",
    "is_correct": "boolean | null",
    "difficulty": "integer (1 to 5)",
    "time_taken_seconds": "float (>= 0.0)",
    "hints_used_count": "integer (>= 0)",
    "highest_hint_level": "integer (0, 1, 2, 3)",
    "remaining_player_health": "integer (>= 0)",
    "attempt_number": "integer (>= 1)"
  },
  "client_timestamp": "string (ISO 8601 UTC timestamp)"
}
```

---

## 4. Concrete Example: Question Answered Event

```json
{
  "version": "1.0.0",
  "event_id": "8f3e5b12-9c42-4f10-b9e7-5782049d5a11",
  "student_id": "std-usr-adarsh-001",
  "session_id": "sess-20260926-1400",
  "mission_id": "OS-CPU-001",
  "concept_id": "cpu_scheduling_fcfs",
  "event_type": "QUESTION_ANSWERED",
  "payload": {
    "challenge_id": "CHAL-FCFS-001",
    "selected_option_id": "A",
    "is_correct": true,
    "difficulty": 2,
    "time_taken_seconds": 14.8,
    "hints_used_count": 1,
    "highest_hint_level": 1,
    "remaining_player_health": 85,
    "attempt_number": 1
  },
  "client_timestamp": "2026-09-26T14:32:00.123Z"
}
```

---

## 5. Delivery & Ingestion Guarantees
1. **At-least-once delivery**: The Game Engine buffers events locally in case of brief connectivity drops and flushes upon reconnection.
2. **Idempotency**: The AI Engine deduplicates incoming events using `event_id`.
3. **Stateless Processing**: Each event carries full contextual identifiers (`student_id`, `mission_id`, `concept_id`) allowing parallel ingestion without distributed lock contention.
