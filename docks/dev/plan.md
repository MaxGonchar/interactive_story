# Implementation Plan

## Scope
This plan covers MVP delivery only.
Post-MVP roadmap is listed separately at the bottom.

---

## Milestones

### M1 — Project Skeleton

**Goal:** Runnable project with empty structure and health check.

**Entry criteria:**
- Architecture and package layout finalized (`progect_structure.md` DONE)
- Dev environment requirements known

**Deliverables:**
- Backend: FastAPI app boots, `GET /health` returns 200
- Backend: package layout created (`app/api`, `app/services`, `app/repositories`, `app/llm`, `app/models`, `app/utils`)
- Frontend: React app boots, renders index page with placeholder text
- Scripts: `install.sh` and `run.sh` (or `Makefile`) work for both BE and FE
- Config: `.env.example` with required keys documented

**Exit criteria:**
- `GET /health` returns `{"status": "ok"}`
- Frontend index page loads in browser without errors
- Both apps start from a single command

**Dependencies:** none

**Test gate:** none (manual smoke test)

---

### M2 — API Contract Stubs

**Goal:** All MVP endpoints exist and return hardcoded valid responses. No logic, no storage.

**Entry criteria:** M1 complete

**Deliverables:**
- All 7 MVP endpoints registered in routers:
  - `GET /stories`
  - `GET /stories/{story_id}`
  - `GET /stories/{story_id}/scenes/{scene_id}`
  - `POST /stories/{story_id}/scenes/{scene_id}/play`
  - `PUT /stories/{story_id}/scenes/{scene_id}/messages/{message_id}`
  - `DELETE /stories/{story_id}/scenes/{scene_id}/messages/{message_id}`
  - `POST /stories/{story_id}/scenes/{scene_id}/finish`
- Request/response Pydantic models defined (`app/models/api.py`)
- Input validation in place (Pydantic)
- Standard error response model (`ErrorResponse`) defined and used
- Hardcoded stub responses match `endpoints.md` shapes exactly

**Exit criteria:**
- All 7 endpoints return correct HTTP status codes with valid response shapes
- Invalid input returns 422 with structured error

**Dependencies:** M1

**Test gate:** none (manual curl/Swagger UI check)

---

### M3 — Frontend UI Pages (Mocked)

**Goal:** All MVP pages render with mocked API data. No real API calls.

**Entry criteria:** M2 complete (contracts locked, response shapes known)

**Deliverables:**
- Pages: `StoriesPage`, `StoryPage`, `ScenePage` implemented
- Components: `StoryList`, `SceneList`, `SceneHeader`, `MessageList`, `MessageItem`, `MessageComposer`, `SceneActions`
- API client modules (`api/stories.js`, `api/scenes.js`) defined with mocked return values
- Navigation between pages working
- Scene page renders message list, composer input, and finish-scene button

**Exit criteria:**
- All three pages render without errors
- User can navigate: stories list → story detail → scene view
- Composer input is visible and accepts text
- Finish-scene button is visible on active scenes

**Dependencies:** M2 (for confirmed payload shapes)

**Test gate:** none (manual browser check)

---

### M4 — Data Access Layer

**Goal:** Repositories read and write YAML files according to the storage schema.

**Entry criteria:** M3 complete; `data_storage_structure.md` DONE

**Deliverables:**
- Utilities: `file_paths.py`, `yaml_storage.py`, `atomic_write.py`
- Domain models defined (`app/models/domain.py`, `app/models/storage.py`)
- Repositories implemented:
  - `StoryRepository`: read index, read story metadata
  - `SceneRepository`: read metadata, read messages, write metadata, write messages, update message, delete message
  - `CharacterRepository`: read character card
- Repositories return domain objects, not raw dicts
- Sample YAML fixture files for one story with one scene created under `data/`

**Exit criteria:**
- Repositories can load the fixture files and return correct domain objects
- Atomic write is used for all write operations
- Delete and update operations preserve other messages

**Dependencies:** M3

**Test gate:** unit tests for all repository methods (read, write, update, delete) against fixture files

---

### M5 — LLM Adapter

**Goal:** LLM client sends a constructed prompt to the model and returns a text response.

**Entry criteria:** M4 complete

**Deliverables:**
- `app/llm/prompt_builder.py`: assembles system prompt from scene context (description, character cards, message history)
- `app/llm/scene_llm_client.py`: sends assembled prompt via LangChain, returns assistant reply text
- `app/llm/models.py`: input/output types for the LLM layer
- LangChain used only for prompt templating and model invocation
- Model and API key configurable via environment variables

**Exit criteria:**
- `SceneLLMClient` can be called with scene context and user message, returns a non-empty string
- Works end-to-end against a real model (manual integration test)

**Dependencies:** M4

**Test gate:** unit tests for `PromptBuilder` with mock input; integration test for `SceneLLMClient` (can be skipped in CI if API key unavailable)

---

### M6 — Services and Full Integration

**Goal:** All services implemented. Frontend calls real API. MVP is end-to-end functional.

**Entry criteria:** M4 and M5 complete

**Deliverables:**
- Services implemented:
  - `StoryQueryService`: list stories, get story with scene statuses
  - `SceneQueryService`: get scene with message history
  - `ScenePlayService`: validate active scene, gather context, call LLM adapter, persist both messages atomically
  - `SceneMessageService`: edit message, delete message (active scene only)
  - `SceneLifecycleService`: finish scene, persist summary
- API routers wired to services via FastAPI dependency injection (`dependencies.py`)
- Frontend API client functions replaced with real HTTP calls
- CORS configured for local dev

**Exit criteria:**
- User can open stories list (reads from YAML)
- User can open a story and see its scenes
- User can open the last scene and see messages
- User can send a message and receive an LLM response
- User can edit and delete messages in active scene
- User can finish the scene
- Edit and delete are blocked on finished scenes (returns 409)

**Dependencies:** M4, M5

**Test gate:**
- Unit tests for each service (mock repositories and LLM adapter)
- End-to-end manual walkthrough of full user flow

---

## Milestone Summary

| Milestone | Deliverable                  | Depends on | Test gate              |
|-----------|------------------------------|------------|------------------------|
| M1        | Project skeleton             | —          | Manual smoke           |
| M2        | API stubs                    | M1         | Manual Swagger/curl    |
| M3        | Frontend UI (mocked)         | M2         | Manual browser         |
| M4        | Data access layer            | M3         | Unit tests             |
| M5        | LLM adapter                  | M4         | Unit tests + manual    |
| M6        | Services + full integration  | M4, M5     | Unit tests + E2E walk  |

---

## Post-MVP Roadmap

Features explicitly out of MVP scope, to be planned separately:

- Story creation and editing via UI
- Scene creation and editing via UI
- Character creation and editing via UI
- Multiple active scenes / branching
- Scene replay or history navigation
- User authentication
- Deployment / production infrastructure
