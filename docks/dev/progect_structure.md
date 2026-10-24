# Project Structure and Architecture

This document describes the current implementation. User-visible behavior is documented in `requirements.md`; HTTP endpoints and payloads are documented in `endpoints.md`.

## Backend

The backend uses a layered structure. FastAPI routers handle HTTP requests and responses, services implement use cases, repositories load and persist application data, and LLM clients handle model interactions. `main.py` registers routers and application-level exception handlers; `api/dependencies.py` constructs services and their dependencies.

```text
backend/app/
  api/
    dependencies.py
    routers/
      character_play.py
      characters.py
      choice_driven.py
      models.py
      scenes.py
      stories.py
  exceptions.py
  llm/
    choice_engine_client.py
    character_agent_client.py
    narrator_client.py
    memory_agent_client.py
    logging_config.py
    models.py
    model_factory.py
    prompt_builder.py
    scene_llm_client.py
    story_engine_client.py
    summarize_llm_client.py
    templates/character_driven/
    templates/
    venice_ai.py
    venice_client.py
  main.py
  models/
    api.py
    domain.py
    storage.py
  repositories/
    character_driven_scene_repository.py
    character_repository.py
    choice_driven_story_repository.py
    llm_usage_repository.py
    model_registry_repository.py
    scene_repository.py
    story_repository.py
  services/
    character_driven_scene_creation_service.py
    character_driven_scene_finish_service.py
    character_driven_scene_item_service.py
    character_driven_scene_memory_service.py
    character_driven_scene_query_service.py
    character_driven_scene_summary_service.py
    character_driven_scene_turn_service.py
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

- `api/routers/` defines routes for stories, scene play, character-driven play, choice-driven play, characters, and configured models. `api/dependencies.py` wires repositories, LLM clients, and services.
- `services/` coordinates scene creation, querying, turns, replacement, editing, deletion, summary/memory drafting and finishing; choice-driven play; model registry access; and LLM usage recording.
- `repositories/` translate between domain models and YAML-backed story data. Character-driven scene items use a dedicated repository; character definitions and their accumulated memories use `CharacterRepository`.
- `llm/` builds prompts and invokes scene, character-agent, narrator, memory, summary, story, and choice model operations. Character-driven prompts are in `llm/templates/character_driven/`. `VeniceAIChatModel` adapts the Venice client to LangChain's chat-model interface.
- `models/` separates API schemas, domain objects, and storage schemas.
- `utils/` provides YAML I/O, canonical data paths, and atomic file writes. `exceptions.py` defines application/domain errors; `main.py` maps them to HTTP responses.

Scene play is coordinated by `ScenePlayService`; choice-driven progression is coordinated separately by `ChoiceDrivenPlayService`. In scene play, the user and assistant messages are saved together in one atomic messages-file write after a successful model response. LLM usage is recorded separately, so that usage record is not part of the same atomic write.

Character-driven play is coordinated by separate services for creation, querying, turns, item actions, drafts, and finishing. A player turn calls the narrator; a character turn calls the character agent and then the narrator. A completed turn or replacement is written as one item only after its required model calls succeed. Finishing saves the reviewed summary and participant memory updates; drafts are returned without saving their content.

## Frontend

The frontend is a React application with route-level pages, shared components, and API modules grouped by resource or workflow. Pages own their request and interaction state; shared API functions call the backend.

```text
frontend/src/
  App.jsx
  api/
    character_play.js
    characters.js
    choice_driven.js
    models.js
    scenes.js
    stories.js
  components/
    BulletTextarea.jsx
    CharacterCheckboxList.jsx
    CharacterFinishModal.jsx
    CharacterSelect.jsx
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
    StoryItem.jsx
    StoryTimeline.jsx
    StepItem.jsx
    StoryList.jsx
    icons.jsx
  index.css
  main.jsx
  pages/
    ChoiceDrivenStoryPage.jsx
    NewScenePage.jsx
    NewCharacterScenePage.jsx
    CharacterScenePage.jsx
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

### Character-driven play

1. `character_play.py` handles character-driven scene creation and read requests, then delegates turn, item, draft, and finish operations to their injected services.
2. `CharacterDrivenSceneTurnService` loads scene history and participants. Player turns invoke `NarratorClient`; character turns invoke `CharacterAgentClient` and then `NarratorClient`.
3. A complete turn item is persisted by `CharacterDrivenSceneRepository` after generation succeeds. Replacement updates the latest item in place; edit changes its narration and delete removes only the latest non-opening item.
4. Summary and memory draft services return generated text without saving it to scene or character data. Finish persists the submitted summary and participant memory updates through the scene and character repositories, then marks the scene finished.
5. `api/character_play.js` connects the routes to `NewCharacterScenePage` and `CharacterScenePage`; the latter renders the story timeline, turn composer, and finish review modal.

### Choice-driven progression

1. `choice_driven.py` delegates reads and actions to `ChoiceDrivenPlayService`.
2. The service reads story metadata, step history, and character data; it invokes `ChoiceEngineClient` to generate choices or `StoryEngineClient` to generate the next step.
3. `ChoiceDrivenStoryRepository` persists choice and step changes to the story's YAML-backed history.
4. `api/choice_driven.js` connects the page to these routes, and `ChoiceDrivenStoryPage` updates the displayed steps and choices.

## Dependency Direction

The intended direction is routers to services, services to repositories and LLM clients, and repositories to models and storage utilities. `main.py` and `api/dependencies.py` act as composition and framework boundaries. Shared lower-level modules should not depend on route handlers or page components.

## Tests

- Backend tests are organized by area under `backend/tests/`, including API, functional, LLM, model, repository, service, and utility tests.
- `backend/tests/api/test_character_play_router.py` checks character-driven route payloads and error responses. `backend/tests/functional/test_character_driven_story_flow.py` exercises the complete HTTP lifecycle with temporary story data and deterministic model clients.
- Frontend tests use Vitest and Testing Library and live alongside the component, page, and API modules they cover; shared setup and factories live under `frontend/src/tests/`.
