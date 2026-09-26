# Game Engine — Dasarth 🎮

## Ownership & Domain
**Owner**: Dasarth (Game Engine Lead)

This directory houses the interactive gameplay simulation and rendering engine for ARCANA-AI. The Game Engine consumes structured `GameSpecification` payloads from the AI Engine and executes gameplay mechanics (movement, challenges, dialogue, combat, rewards) while streaming `GameEvent` telemetry back.

## Strict Boundaries
### The Game Engine OWNS:
- Game loop, tick updates, and delta-time processing.
- Player controller, movement physics, jumping, and collision detection.
- Tilemap and level layout rendering.
- NPC presentation, dialogue interaction triggers, and quest tracking.
- Boss encounter mechanics (shields, attack phases, override consoles).
- Player vitals (health, XP, knowledge coin counters).
- Emitting real-time `GameEvent` telemetry strictly adhering to `shared/schemas/game_event.py`.

### The Game Engine DOES NOT OWN:
- Educational mastery calculations or adaptive difficulty logic (owned by Adarsh).
- Hardcoding educational questions or dialogues into source code.
- General application screens and account management (owned by Jeenth).
- Direct database persistence (owned by Abhishek).

## Contract Interfaces
1. **Input**: Consumes `shared/schemas/game_specification.py` (or `shared/types/contracts.d.ts`).
2. **Output**: Produces `shared/schemas/game_event.py` (or `shared/types/contracts.d.ts`).

Refer to [`shared/contracts/ai-game.md`](../shared/contracts/ai-game.md) and [`shared/contracts/game-ai.md`](../shared/contracts/game-ai.md) for full specifications.
