# Project Structure and Architecture

This document describes the current implementation. User-visible behavior is documented in `requirements.md`; HTTP endpoints and payloads are documented in `endpoints.md`.

## Backend

The backend uses a layered structure. FastAPI routers handle HTTP requests and responses, services implement use cases, repositories load and persist application data, and LLM clients handle model interactions. `main.py` registers routers and application-level exception handlers; `api/dependencies.py` constructs services and their dependencies.

```text
backend/app/
  api/
    dependencies.py
    routers/
      characters.py
      choice_driven.py
      models.py
      scenes.py
      stories.py
  exceptions.py
  llm/
    choice_engine_client.py
    logging_config.py
    models.py
    prompt_builder.py
    scene_llm_client.py
    story_engine_client.py
    summarize_llm_client.py
    templates/
    venice_ai.py
    venice_client.py
  main.py
  models/
    api.py
    domain.py
    storage.py
  repositories/
    character_repository.py
    choice_driven_story_repository.py
    llm_usage_repository.py
    model_registry_repository.py
    scene_repository.py
    story_repository.py
  services/
    choice_driven_play_service.py
    llm_usage_service.py
    model_registry_service.py
    scene_creation_service.py
    scene_lifecycle_service.py
    scene_message_service.py
    scene_play_service.py
    scene_query_service.py
    scene_summarize_service.py
    story_query_service.py
  utils/
    atomic_write.py
    file_paths.py
    yaml_storage.py
```

### Responsibilities

- `api/routers/` defines routes for stories, scenes, choice-driven play, characters, and configured models. `api/dependencies.py` wires repositories, LLM clients, and services.
- `services/` coordinates use cases, including scene creation, querying, playing, summarizing, finishing, and message management; choice-driven play; model registry access; and LLM usage recording.
- `repositories/` translate between domain models and YAML-backed story data. The usage and model-registry repositories handle their respective stored records.
- `llm/` builds prompts and invokes the scene, summary, story, and choice model operations. `VeniceAIChatModel` adapts the Venice client to LangChain's chat-model interface.
- `models/` separates API schemas, domain objects, and storage schemas.
- `utils/` provides YAML I/O, canonical data paths, and atomic file writes. `exceptions.py` defines application/domain errors; `main.py` maps them to HTTP responses.

Scene play is coordinated by `ScenePlayService`; choice-driven progression is coordinated separately by `ChoiceDrivenPlayService`. In scene play, the user and assistant messages are saved together in one atomic messages-file write after a successful model response. LLM usage is recorded separately, so that usage record is not part of the same atomic write.

## Frontend

The frontend is a React application with route-level pages, shared components, and API modules grouped by resource or workflow. Pages own their request and interaction state; shared API functions call the backend.

```text
frontend/src/
  App.jsx
  api/
    characters.js
    choice_driven.js
    models.js
    scenes.js
    stories.js
  components/
    BulletTextarea.jsx
    ChoicesGrid.jsx
    FinishModal.jsx
    MessageComposer.jsx
    MessageItem.jsx
    MessageList.jsx
    NavBar.jsx
    ProcessingLabel.jsx
    ResponseTimeIndicator.jsx
    SceneActions.jsx
    SceneHeader.jsx
    SceneList.jsx
    StepItem.jsx
    StoryList.jsx
    icons.jsx
  index.css
  main.jsx
  pages/
    ChoiceDrivenStoryPage.jsx
    NewScenePage.jsx
    ScenePage.jsx
    StoriesPage.jsx
    StoryPage.jsx
  styles.js
  tests/
    factories.js
    setup.js
```

Component and API-module test files are colocated with the modules they cover. Page tests are colocated in `pages/`; shared test setup and factories live in `tests/`.

## Request Flows

### Scene play

1. `scenes.py` validates and handles the play request, delegating to `ScenePlayService` through dependency injection.
2. The service reads scene state, messages, character data, and the model registry, then builds the LLM context and invokes `SceneLLMClient`.
3. If the model call succeeds, the service appends the user and assistant messages in a single atomic write and records LLM usage separately.
4. The router shapes the response; `api/scenes.js` returns it to `ScenePage`, which updates the chat state.

### Choice-driven progression

1. `choice_driven.py` delegates reads and actions to `ChoiceDrivenPlayService`.
2. The service reads story metadata, step history, and character data; it invokes `ChoiceEngineClient` to generate choices or `StoryEngineClient` to generate the next step.
3. `ChoiceDrivenStoryRepository` persists choice and step changes to the story's YAML-backed history.
4. `api/choice_driven.js` connects the page to these routes, and `ChoiceDrivenStoryPage` updates the displayed steps and choices.

## Dependency Direction

The intended direction is routers to services, services to repositories and LLM clients, and repositories to models and storage utilities. `main.py` and `api/dependencies.py` act as composition and framework boundaries. Shared lower-level modules should not depend on route handlers or page components.

## Tests

- Backend tests are organized by area under `backend/tests/`, including API, functional, LLM, model, repository, service, and utility tests.
- Frontend tests use Vitest and Testing Library and live alongside the component, page, and API modules they cover; shared setup and factories live under `frontend/src/tests/`.
- `StoryListResponse`
