# Shared Contract: AI Engine ➔ Game Engine (`ai-game.md`)

**Contract Version**: `v1.0.0`  
**Producers**: AI Engine (Adarsh)  
**Consumers**: Game Engine (Dasarth), Frontend (Jeenth)  
**Schema Implementation**: [`shared/schemas/game_specification.py`](../schemas/game_specification.py)  
**Type Definitions**: [`shared/types/contracts.d.ts`](../types/contracts.d.ts)

---

## 1. Overview
The AI Engine produces a `GameSpecification` payload that directs what educational content the Game Engine presents, what challenges the player must solve, what dialogue NPCs speak, and what rewards are granted.

> [!IMPORTANT]
> The AI Engine **never** dictates coordinates, sprite animations, physics vectors, or render frames. It specifies *educational intent* and *gameplay objectives*. The Game Engine determines how to render and simulate the level.

---

## 2. Specification Payload Schema

```json
{
  "$schema": "https://arcana-ai.org/schemas/v1/game-specification.json",
  "version": "1.0.0",
  "mission_id": "string (UUID or formatted ID, e.g. OS-SCHED-001)",
  "concept_id": "string (e.g. cpu_scheduling_fcfs)",
  "title": "string (Human-readable mission title)",
  "difficulty": "integer (1 to 5)",
  "learning_objective": "string (Actionable educational objective)",
  "narrative": {
    "zone_theme": "string (e.g. cyber_core, crystal_archives, neon_foundry)",
    "mission_intro": "string (Story context for the player)"
  },
  "npc": {
    "npc_id": "string (e.g. grand_scribe_alan)",
    "npc_name": "string (e.g. Grand Scribe Alan)",
    "dialogue": [
      "string (Paragraph 1 of NPC speech / explanation)",
      "string (Paragraph 2...)"
    ],
    "lore_snippet": "string (Optional backstory / flavor text)"
  },
  "challenge": {
    "challenge_id": "string (e.g. CHAL-FCFS-01)",
    "challenge_type": "string (mcq | concept_puzzle | boss_override | calculation)",
    "prompt": "string (Question or problem statement)",
    "options": [
      {
        "id": "string (e.g. A, B, C, D)",
        "text": "string (Option content)"
      }
    ],
    "correct_option_id": "string (e.g. A)",
    "hints": [
      {
        "level": 1,
        "type": "nudge",
        "text": "string (First gentle clue)"
      },
      {
        "level": 2,
        "type": "guidance",
        "text": "string (More explicit conceptual hint)"
      },
      {
        "level": 3,
        "type": "scaffold",
        "text": "string (Step-by-step guidance without giving direct answer)"
      }
    ],
    "explanation": "string (Complete educational explanation revealed on completion)"
  },
  "boss": {
    "is_boss_mission": "boolean",
    "boss_id": "string | null",
    "boss_name": "string | null",
    "shield_weakness_concept": "string | null",
    "phases": "integer (default 1)"
  },
  "reward": {
    "xp": "integer (>= 0)",
    "knowledge_coins": "integer (>= 0)",
    "mastery_boost_potential": "float (0.0 to 1.0)"
  },
  "metadata": {
    "source_document_id": "string (UUID of ingested source material)",
    "chunk_ids": ["string (Source chunks used for grounding)"],
    "generated_at": "string (ISO 8601 timestamp)",
    "generator_model": "string (e.g. gemini-2.5-flash)"
  }
}
```

---

## 3. Concrete Example: CPU Scheduling FCFS Mission

```json
{
  "version": "1.0.0",
  "mission_id": "OS-CPU-001",
  "concept_id": "cpu_scheduling_fcfs",
  "title": "The Queue of the Ancients",
  "difficulty": 2,
  "learning_objective": "Understand First-Come, First-Served (FCFS) process ordering and identify the Convoy Effect.",
  "narrative": {
    "zone_theme": "cyber_core",
    "mission_intro": "The Kernel mainframe is congested. Process buffers are stalling behind a massive compute task."
  },
  "npc": {
    "npc_id": "grand_scribe_alan",
    "npc_name": "Grand Scribe Alan",
    "dialogue": [
      "Greetings, traveler. In the First-Come, First-Served scheduling algorithm, processes are executed strictly in the order of their arrival.",
      "While simple and non-preemptive, beware of long CPU bursts blocking shorter tasks ahead—a phenomenon known as the Convoy Effect."
    ],
    "lore_snippet": "Alan has overseen the execution queues since the First Epoch of Silicon."
  },
  "challenge": {
    "challenge_id": "CHAL-FCFS-001",
    "challenge_type": "mcq",
    "prompt": "What major drawback occurs in FCFS scheduling when a long CPU-intensive process arrives before several short processes?",
    "options": [
      {
        "id": "A",
        "text": "The Convoy Effect, causing average waiting time to dramatically increase"
      },
      {
        "id": "B",
        "text": "Frequent preemption causing high context-switch overhead"
      },
      {
        "id": "C",
        "text": "Complete deadlock between threads"
      },
      {
        "id": "D",
        "text": "Priority inversion in real-time tasks"
      }
    ],
    "correct_option_id": "A",
    "hints": [
      {
        "level": 1,
        "type": "nudge",
        "text": "Think of vehicles stuck behind a slow-moving truck on a single-lane road."
      },
      {
        "level": 2,
        "type": "guidance",
        "text": "FCFS does not preempt running processes, so short jobs must wait until the large job completes."
      },
      {
        "level": 3,
        "type": "scaffold",
        "text": "This traffic-jam phenomenon is named after a line of traveling vehicles."
      }
    ],
    "explanation": "In FCFS, because execution is non-preemptive, a long burst process occupies the CPU while all short processes wait in line. This is the Convoy Effect, which significantly degrades average waiting time."
  },
  "boss": {
    "is_boss_mission": false,
    "boss_id": null,
    "boss_name": null,
    "shield_weakness_concept": null,
    "phases": 1
  },
  "reward": {
    "xp": 150,
    "knowledge_coins": 25,
    "mastery_boost_potential": 0.15
  },
  "metadata": {
    "source_document_id": "doc-os-silberschatz-ch5",
    "chunk_ids": ["chunk-os-sched-014", "chunk-os-sched-015"],
    "generated_at": "2026-09-26T12:00:00Z",
    "generator_model": "gemini-2.5-flash"
  }
}
```

---

## 4. Validation Rules
1. `difficulty` must be an integer between `1` (Very Easy) and `5` (Very Hard).
2. `challenge.options` must contain at least 2 options and at most 6 options.
3. `challenge.correct_option_id` must match one of the IDs in `challenge.options`.
4. `challenge.hints` must be strictly ordered by level (`1`, `2`, `3`).
5. `reward.xp` and `reward.knowledge_coins` must be non-negative.
