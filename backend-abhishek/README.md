# Backend Infrastructure — Abhishek 🗄️⚡

## Ownership & Domain
**Owner**: Abhishek (Backend / Database / Storage Lead)

This directory houses the backend services, relational/document persistence, object storage, and authentication infrastructure that support the ARCANA-AI ecosystem.

## Strict Boundaries
### The Backend OWNS:
- Relational database schema design (users, profiles, progress, sessions, audit logs).
- Document and asset file storage (raw PDFs, processed text, audio, images).
- User authentication, JWT issuance, session management, and role-based access.
- CRUD APIs for learner metadata, persistent game states, and event history.
- Asynchronous task queues / background worker infrastructure for document processing.
- Health checks, database migrations, connection pooling, and backup procedures.

### The Backend DOES NOT OWN:
- Semantic chunking, embeddings, or RAG intelligence (owned by Adarsh).
- Mastery scoring algorithms or adaptive curriculum planning (owned by Adarsh).
- Game physics or game loop state (owned by Dasarth).
- Frontend UI rendering (owned by Jeenth).

## Integration Interfaces
- Interacts with AI Engine through versioned internal endpoints (`/api/v1/...`).
- Provides database models and persistence hooks for user profiles and event history.
