# Purpose
Build a local web app that automates the interactive story playing process.

Today the full flow is executed manually in one LLM service.
For MVP we move only the core logic (scene playing) into this app and keep between-scene updates manual.

# Product Context
- Main value: playing scenes in-app (this is the core fun and primary user goal).
- MVP should be intentionally small to enable fast usage and learning.
- Post-MVP features are informed by real usage and flow adjustments.

# Functional Requirements (MVP)
The app must support:
- can see stories list
- can open a story and see scenes list
- can open the last scene and see messages
- can play the scene by sending a message and receiving a response from the assistant
- can edit a message in the current active scene
- can delete a message in the current active scene
- can finish the scene

# Out of Scope for MVP (Post-MVP)
- create or update story content via UI/API
- create new scenes in app
- update scene metadata/content between scenes in app
- update character definitions in app
- update scene character subsets in app
- update scene descriptions in app
- regenerate or edit scene summaries in app
- automated between-scene flow steps from the diagram (character/state updates, summary refinements, prompt evolution)
- advanced message history management beyond edit and delete in the current active scene

# Domain Definitions
- Story: top-level narrative container with title, ordered scenes, and references to character cards.
- Story Character: character definition stored as a separate character card file inside a story.
- Scene: one playable episode in a story. Has status (`active` or `finished`), ordered messages, scene description, and a subset of story characters.
- Message: chat item in a scene with role (`user` or `assistant`) and textual content.
- Scene Description: structured scene context with entry point, guide, and writing style.
- Finished scene: scene that no longer accepts new user messages via the play endpoint and has a scene summary.

# Non-Functional Requirements (MVP)
## General
- client-server architecture
- REST API
- local-first usage (single user on local machine)

## Performance Baseline (local environment)
- `GET /stories`, `GET /stories/{story_id}`, `GET /stories/{story_id}/scenes/{scene_id}`: p95 <= 500 ms (excluding frontend rendering)
- scene play operation (user message to assistant response): p95 <= 20 s, excluding external LLM provider outages
- app startup to healthy state: <= 10 s

## Reliability
- all file writes must be atomic to avoid partial/corrupted YAML files
- invalid input must return deterministic 4xx responses with error details
- failed LLM call must not corrupt scene history

## Observability
- structured logs for requests, validation errors, repository errors, and LLM call failures

## BE Stack
- Python
- FastAPI
- LLM operations: LangChain
- storage: disk space, YAML files

## FE Stack
- React

# Conventions
## Python
- type hints
- async functions for I/O operations
- Pydantic models (request/response models, data models, LLM operation models)
- dependency injection (services, repositories)

## JavaScript
- keep frontend code modular and API-contract driven
