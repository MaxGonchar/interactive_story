# Project Structure (MVP)

## Architecture Decisions

### Backend architectural style
Use layered architecture with clear responsibilities:
- API layer: FastAPI routers, request parsing, response shaping, HTTP error mapping
- Service layer: business rules and use-case orchestration
- Repository layer: YAML file read/write and storage validation
- LLM adapter layer: prompt construction input assembly and LangChain integration
- Shared utilities: file operations, path resolution, logging helpers

### Data access pattern
Use the Repository pattern.

Why Repository over DAO:
- storage is file-based and domain-shaped rather than table-shaped
- repositories map directly to MVP aggregates: stories, scenes, messages, characters
- service layer should work with domain objects, not file-level persistence details

### Service design
Use focused application services rather than one large orchestrator.

Recommended services:
- `StoryQueryService`
  - list stories
  - get story with scene statuses
- `SceneQueryService`
  - get scene details and message history
- `ScenePlayService`
  - validate scene is active
  - gather scene context
  - call LLM adapter
  - persist user and assistant messages atomically
- `SceneMessageService`
  - edit message in active scene
  - delete message in active scene
- `SceneLifecycleService`
  - finish scene and persist summary

Decision on orchestrator:
- no global orchestrator for MVP
- `ScenePlayService` is the only use-case that coordinates multiple dependencies and acts as the local orchestrator for scene play

### LangChain usage
Use LangChain as a thin LLM integration layer, not as the application architecture.

Use in MVP:
- prompt templating / message assembly
- model invocation abstraction
- structured boundary for future provider changes

Do not use in MVP:
- agents
- tools
- multi-step chains with branching control flow
- autonomous planning abstractions

Reason:
- MVP flow is deterministic and request-response based
- extra LangChain abstractions would add complexity without solving a current problem

## Backend Module Boundaries

### Suggested backend package layout

```text
backend/
  app/
    api/
      routers/
        stories.py
        scenes.py
      dependencies.py
      errors.py
    services/
      story_query_service.py
      scene_query_service.py
      scene_play_service.py
      scene_message_service.py
      scene_lifecycle_service.py
    repositories/
      story_repository.py
      scene_repository.py
      character_repository.py
    llm/
      prompt_builder.py
      scene_llm_client.py
      models.py
    models/
      api.py
      domain.py
      storage.py
    utils/
      file_paths.py
      yaml_storage.py
      atomic_write.py
      logging.py
    main.py
```

### API routers
- `stories.py`
  - `GET /stories`
  - `GET /stories/{story_id}`
- `scenes.py`
  - `GET /stories/{story_id}/scenes/{scene_id}`
  - `POST /stories/{story_id}/scenes/{scene_id}/play`
  - `PUT /stories/{story_id}/scenes/{scene_id}/messages/{message_id}`
  - `DELETE /stories/{story_id}/scenes/{scene_id}/messages/{message_id}`
  - `POST /stories/{story_id}/scenes/{scene_id}/finish`

### Repositories
- `StoryRepository`
  - read stories index
  - read story metadata
- `SceneRepository`
  - read scene metadata
  - read scene messages
  - write scene metadata
  - write scene messages
  - update message content
  - delete message by id
- `CharacterRepository`
  - read character cards referenced by story / scene

Repository rule:
- repositories do not call LLMs
- repositories do not contain HTTP concepts

### Domain models
Suggested domain entities:
- `Story`
- `StoryListItem`
- `Scene`
- `SceneDescription`
- `Message`
- `CharacterCard`

### API models
Suggested request/response models:
- `StoryListResponse`
- `StoryDetailResponse`
- `SceneDetailResponse`
- `PlaySceneRequest`
- `PlaySceneResponse`
- `UpdateMessageRequest`
- `MessageResponse`
- `FinishSceneRequest`
- `FinishSceneResponse`
- `ErrorResponse`

### Utilities
Keep utilities narrow and non-domain-specific:
- `file_paths.py`
  - build canonical paths for story, scene, character, metadata, messages files
- `yaml_storage.py`
  - load/serialize YAML
- `atomic_write.py`
  - temp-file write + rename logic
- `logging.py`
  - logger setup helpers

Avoid premature utils:
- no generic file manipulator abstraction
- no generic web client unless an external HTTP integration actually appears

## Frontend Structure

### Frontend architectural style
Use page-level data fetching with a thin API client and local UI state.

State decision for MVP:
- no global state manager required
- use React component state and route-level loading
- refetch scene data after operations when needed

### Suggested frontend package layout

```text
frontend/
  src/
    app/
      routes/
        StoriesPage.jsx
        StoryPage.jsx
        ScenePage.jsx
    components/
      StoryList.jsx
      SceneList.jsx
      SceneHeader.jsx
      MessageList.jsx
      MessageItem.jsx
      MessageComposer.jsx
      SceneActions.jsx
    api/
      stories.js
      scenes.js
    types/
      api.js
    utils/
      http.js
      errors.js
    main.jsx
```

### Frontend pages
- `StoriesPage`
  - display stories list
- `StoryPage`
  - display story title and scene statuses
- `ScenePage`
  - display scene description
  - display message history
  - play scene
  - edit/delete message
  - finish scene

### Frontend component responsibilities
- `StoryList`
  - render clickable story list
- `SceneList`
  - render ordered scenes with finished status
- `SceneHeader`
  - render scene description and summary when present
- `MessageList`
  - render ordered messages
- `MessageItem`
  - render one message and expose edit/delete actions when scene is active
- `MessageComposer`
  - submit play request
- `SceneActions`
  - finish scene action

### API client modules
- `api/stories.js`
  - `getStories()`
  - `getStory(storyId)`
- `api/scenes.js`
  - `getScene(storyId, sceneId)`
  - `playScene(storyId, sceneId, content)`
  - `updateMessage(storyId, sceneId, messageId, content)`
  - `deleteMessage(storyId, sceneId, messageId)`
  - `finishScene(storyId, sceneId, sceneSummary)`

## Request Flow Example

### Play scene request flow
1. Client calls `POST /api/stories/{story_id}/scenes/{scene_id}/play`.
2. Scene router validates request model and forwards to `ScenePlayService`.
3. `ScenePlayService` loads scene metadata and message history from `SceneRepository`.
4. `ScenePlayService` loads referenced character cards from `CharacterRepository`.
5. `ScenePlayService` assembles prompt input for `SceneLlmClient`.
6. `SceneLlmClient` invokes the LLM through LangChain.
7. On success, `ScenePlayService` appends user and assistant messages through `SceneRepository` in one atomic write.
8. Service returns domain result.
9. Router maps domain result to API response.
10. Client appends returned messages to UI.

## Dependency Direction
- routers depend on services
- services depend on repositories and llm adapter
- repositories depend on storage utilities
- llm adapter depends on LangChain and prompt builder
- utilities depend on no application layers

No lower layer may depend on a higher layer.

## Testing Implications
- repository tests validate YAML parsing, atomic writes, message edit/delete semantics
- service tests validate scene rules and LLM failure handling
- API tests validate response contracts and error mapping
- frontend tests validate scene-page interactions for play, edit, delete, and finish
