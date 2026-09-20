# Feature: Scene-Level LLM Picking

**Status**: Draft
**Date**: 2026-09-13

## Summary
Currently the user can only pick which LLM model to use once a scene is already being played, on the `ScenePage`. Scene creation (`NewScenePage`) has no model picker at all, so the first assistant message of a new scene is always generated with whatever model the play-time resolution logic happens to fall back to. This feature moves LLM selection into scene creation: the user picks the model that will generate the scene's first message, the picker defaults to the last model used in the previous scene (or the registry default for the very first scene), and the existing in-scene model switching on `ScenePage` remains unchanged.

## Value
- Removes an extra step/inconsistency: users currently only discover/set their preferred model after a scene already exists.
- Makes model choice deterministic for the scene's opening message instead of relying on implicit fallback resolution.
- Low risk, additive change: fits naturally into the existing scene creation flow without touching MVP-critical play/edit/delete/finish operations.
- Success criteria: creating a new scene always uses an explicit, user-confirmed model for the first message; the picker is pre-filled correctly (default model for the first scene, last-used model for subsequent scenes); in-scene model switching during play continues to work exactly as today.

## Scope
### In scope for first iteration
- Add a required `model_id` field to the scene creation request and validate it against the model registry.
- Store the chosen model on the scene's first (assistant) message via the existing `llm_data.model_id` field — no new storage field/schema needed.
- Add a model picker to `NewScenePage`, pre-filled with:
  - the registry default model when there is no previous scene, or
  - the model from the previous scene's last assistant message when one exists.
- Reject scene creation with a validation error when `model_id` is missing or not present in the registry (same behavior as `play`/`regenerate` today).

### Out of scope / future
- Persisting a separate "preferred model" concept independent of message history.
- Changing in-scene model switching behavior on `ScenePage` (already works and is unaffected).
- Any change to the model registry itself (`GET /api/models`, `data/models.yaml`).

## User Flow
1. User opens `NewScenePage` for a story.
2. Page loads story, characters, model registry, and (if a previous finished scene exists) that scene's detail, same as today.
3. Model picker is pre-filled:
   - No previous scene → registry `default_model_id`.
   - Previous scene exists → the `model_id` from that scene's very last message (`llm_data.model_id`), falling back to registry default if that last message has no `llm_data` (e.g. it is a user message).
4. User may change the pre-filled model before submitting, exactly like they can already change writing style, context, etc.
5. On submit, the selected `model_id` is sent along with the rest of the create-scene payload.
6. Backend validates `model_id` against the registry, creates the scene, and stores the model on the first assistant message's `llm_data`.
7. User is navigated to the new scene. `ScenePage`'s existing model-memory logic (`_resolve_model` walking message history for the latest assistant `llm_data`) now naturally picks up this model as the "last used" value, with no changes required there.
8. During play, the user can still switch models per message as today.

## API Changes
### `POST /api/stories/{story_id}/scenes`
- Request gains a required field: `model_id: string`.
- Validation: `model_id` must exist in the model registry; otherwise the request fails.
- Response shape is unchanged.

**Request**
```json
{
    "user_character_id": "player",
    "character_ids": ["captain-mora"],
    "context": ["..."],
    "general_scene_guide": "...",
    "writing_style": "...",
    "first_message": "...",
    "model_id": "gpt-4.1"
}
```

**Response 422** – validation error (`validation_error`), added case: `model_id` missing or not found in registry (reuses existing `InvalidModelError`, same as `play`/`regenerate`).

## Data Changes
None. `messages.yaml` already supports an optional `llm_data.model_id` per message (see `data_storage_structure.md`); the scene's first assistant message will simply be written with `llm_data` populated at creation time instead of left `null`.

## Backend Changes
- `app/models/api.py` — `CreateSceneRequest` gains `model_id: str`.
- `app/services/scene_creation_service.py` — `SceneCreationService.create(...)`:
  - takes `model_id` as a new parameter,
  - resolves/validates it via `ModelRegistryService` (raising `InvalidModelError` on an unknown id, same as `ScenePlayService._resolve_model`),
  - builds the first `Message` with `llm_data=LLMData(model_id=...)` instead of `llm_data=None`.
- `app/api/routers/scenes.py` — `create_scene` passes `request.model_id` through to the service.
- `app/api/dependencies.py` — `SceneCreationService` needs `ModelRegistryService` injected (currently only takes `StoryRepository` and `SceneRepository`).
- No repository or storage schema changes required.

## Frontend Changes
- `frontend/src/pages/NewScenePage.jsx`:
  - fetch model registry via `getModels()` alongside existing `getStory`/`getCharacters` calls.
  - add `selectedModelId` state, pre-filled from the previous scene's very last message (`sceneData.messages[sceneData.messages.length - 1]?.llm_data?.model_id`, already loading that scene's data for context/writing style) or the registry `default_model_id` when there is no previous scene or the last message has no `llm_data`.
  - render a model `<select>` (reusable structure similar to `SceneHeader`'s model control).
  - include `model_id: selectedModelId` in the `createScene` payload.
- `frontend/src/api/scenes.js` — `createScene` payload already forwards an arbitrary object, no client change needed beyond adding the field when called.
- `frontend/src/pages/NewScenePage.test.jsx` — update existing tests' expected `createScene` payload to include `model_id`, and add tests for: default-model preselection (no previous scene), last-used-model preselection (previous scene with `llm_data`), and user overriding the preselected model.
- `ScenePage.jsx` / `SceneHeader.jsx` — no changes required.

## Open Questions
- None outstanding; all prior open questions (request shape, storage approach, validation behavior) were resolved during discussion.

## Risks
- `SceneCreationService` currently has no dependency on `ModelRegistryService`; wiring it in via `app/api/dependencies.py` is a small but real touch point to get right (must not break existing `SceneCreationService` construction/tests).
- Existing `NewScenePage.test.jsx` assertions on the exact `createScene` payload will break until updated to include `model_id` — must update alongside implementation, not after.
- If a previous scene's very last message has no `llm_data` (e.g. it is a user message, or old data created before this feature), preselection must fall back to the registry default rather than erroring.
