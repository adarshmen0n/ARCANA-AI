# Frontend — Jeenth 💻📱

## Ownership & Domain
**Owner**: Jeenth (Frontend Lead)

This directory houses the client application for ARCANA-AI, providing learners with a modern interface for document uploads, interactive learning paths, AI tutor dialogues, profile statistics, and the launcher for the game client.

## Strict Boundaries
### The Frontend OWNS:
- User onboarding and authentication views.
- Document upload UI with real-time ingestion status tracking.
- Interactive Learning Graph visualizer and mastery dashboards.
- AI Tutor conversational chat interface.
- Launching and bridging the Game Engine instance.
- Client-side state management, routing, and error boundaries.

### The Frontend DOES NOT OWN:
- Educational reasoning or AI prompt logic (owned by Adarsh).
- In-game sprite rendering or collision loops (owned by Dasarth).
- Database tables or server-side auth infrastructure (owned by Abhishek).
- Design system tokens or animation assets (owned by Kruthic).

## Communication Protocols
- Calls Backend REST APIs (`/api/v1/...`).
- Relies on TypeScript contracts in [`shared/types/`](../shared/types/).
