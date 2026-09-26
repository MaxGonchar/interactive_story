# API Contract

## Overview

- API base path: `/api`
- Request and response bodies use JSON unless noted otherwise.
- Error responses use the common shape described below.

## Errors

```json
{
    "error": {
        "code": "string",
        "message": "string"
    }
}
```

Request validation errors return `422` with code `validation_error`. Domain errors return their configured status and error code. Unhandled errors return `500` with code `internal_error`; LLM provider failures return `502` with code `llm_error`. Framework HTTP errors use code `http_error`.

Common domain errors include:

| Status | Code | Meaning |
|---|---|---|
| 404 | `not_found` | Requested story, scene, character, or message was not found. |
| 409 | `scene_finished` | The operation is not allowed on a finished scene. |
| 409 | `active_scene_exists` | A new scene cannot be created while one is unfinished. |
| 409 | `narrator_mode_not_supported` | Narrator mode is only supported for `scene` stories. |
| 409 | `no_steps` | A choice operation requires at least one existing step. |
| 409 | `no_assistant_message` | There is no last assistant message to regenerate. |
| 409 | `no_user_message` | There is no preceding user message to regenerate from. |
| 422 | `validation_error` | The request is invalid or references an unavailable model. |
| 502 | `llm_error` | An upstream language-model request failed. |
| 500 | `internal_error` | An unexpected server or configuration error occurred. |

## Health

### GET /health

Health check. This route is outside the `/api` prefix.

**Response 200**

```json
{"status": "ok"}
```

## Stories and Reference Data

### GET /api/stories

List stories, ordered by `created_at` descending.

**Response 200**

```json
{
    "data": [
        {
            "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
            "title": "The Black Harbor",
            "type": "scene"
        }
    ]
}
```

`type` is `scene` or `choice_driven`.

### GET /api/stories/{story_id}

Return story metadata and its ordered scene references. The scenes are ordered by numeric scene ID. `active_scene_id` is `null` when no scene is unfinished.

**Response 200**

```json
{
    "data": {
        "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        "title": "The Black Harbor",
        "scenes": [
            {"id": 1, "finished": true},
            {"id": 2, "finished": false}
        ],
        "active_scene_id": 2
    }
}
```

**Response 404**: story not found.

### GET /api/stories/{story_id}/characters

List the characters available in a story.

**Response 200**

```json
{
    "data": [
        {"id": "captain", "name": "The Captain"}
    ]
}
```

### GET /api/models

Return configured language models and the default model ID.

**Response 200**

```json
{
    "data": {
        "models": {
            "story-model": {
                "name": "Story Model",
                "providerModelID": "provider/model-name"
            }
        },
        "default_model_id": "story-model"
    }
}
```

## Scene Endpoints

### POST /api/stories/{story_id}/scenes

Create the next scene. Creation is rejected if the story already has an unfinished scene.

**Request**

```json
{
    "user_character_id": "captain",
    "character_ids": ["navigator"],
    "context": ["The ship has reached the harbor."],
    "general_scene_guide": "Keep tension rising.",
    "writing_style": "Cinematic and concise.",
    "first_message": "A bell rings through the fog.",
    "model_id": "story-model"
}
```

`user_character_id` is required but may be `null`. `character_ids` may be omitted and defaults to an empty list. `context` must contain at least one item. A non-null user character cannot also appear in `character_ids`. Every referenced character and the model ID must exist. Narrator mode (`user_character_id: null`) is only supported for `scene` stories.

**Response 201**

```json
{"data": {"id": 3, "finished": false}}
```

**Responses**: `404` for a missing story or character; `409` for an existing active scene or unsupported narrator mode; `422` for invalid request data or unavailable model.

### GET /api/stories/{story_id}/scenes/{scene_id}

Return scene metadata and the full message history. Messages are ordered by ID. `context` and `scene_summary` are nullable; `llm_data` is omitted for messages without model metadata.

**Response 200**

```json
{
    "data": {
        "id": 3,
        "finished": false,
        "scene_description": {
            "general_scene_guide": "Keep tension rising.",
            "writing_style": "Cinematic and concise."
        },
        "scene_summary": null,
        "context": ["The ship has reached the harbor."],
        "messages": [
            {
                "id": 1,
                "role": "assistant",
                "content": "A bell rings through the fog.",
                "llm_data": {"model_id": "story-model"}
            }
        ]
    }
}
```

**Response 404**: story or scene not found.

### POST /api/stories/{story_id}/scenes/{scene_id}/play

Send a user message and receive the assistant response. The selected `model_id` is optional; when omitted, the backend uses the previous assistant message's model when available, otherwise the configured default.

**Request**

```json
{
    "content": "I look for the nearest light source.",
    "model_id": "story-model"
}
```

`content` must contain 1–4000 characters.

**Response 200**

```json
{
    "data": {
        "user_message": {
            "id": 2,
            "role": "user",
            "content": "I look for the nearest light source."
        },
        "assistant_message": {
            "id": 3,
            "role": "assistant",
            "content": "A lantern swings near a wooden post...",
            "llm_data": {"model_id": "story-model"}
        }
    }
}
```

After a successful LLM response, both messages are persisted in one atomic messages-file write. If the LLM call fails, neither message is persisted. LLM usage is recorded separately.

**Responses**: `404` for a missing story or scene; `409` if the scene is finished; `422` for invalid content or unavailable model; `502` if the LLM request fails.

### POST /api/stories/{story_id}/scenes/{scene_id}/regenerate

Regenerate the latest assistant message using the preceding user message. This replaces the existing assistant message rather than adding another message. The request has no body.

**Response 200**

```json
{
    "data": {
        "assistant_message": {
            "id": 3,
            "role": "assistant",
            "content": "A lantern swings near a wooden post...",
            "llm_data": {"model_id": "story-model"}
        }
    }
}
```

**Responses**: `404` for a missing story or scene; `409` if the scene is finished, there is no assistant message to replace, or there is no preceding user message; `502` if the LLM request fails.

### GET /api/stories/{story_id}/scenes/{scene_id}/summarize

Generate and return a scene summary. This endpoint does not finish the scene or save the summary to scene metadata; use the finish endpoint to record a summary.

**Response 200**

```json
{"data": {"summary": ["The hero discovered the map.", "He escaped the harbor."]}}
```

**Responses**: `404` for a missing story or scene; `409` if the scene is finished; `502` if the LLM request fails.

### PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}

Update a message's content. The role and ID are unchanged.

**Request**

```json
{"content": "I carefully inspect the lantern."}
```

`content` must contain 1–4000 characters.

**Response 200**

```json
{"data": {"id": 2, "role": "user", "content": "I carefully inspect the lantern."}}
```

**Responses**: `404` for a missing story, scene, or message; `409` if the scene is finished; `422` for invalid content.

### DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}

Delete a message. Remaining message IDs are not renumbered.

**Response 200**

```json
{"success": true}
```

**Responses**: `404` for a missing story, scene, or message; `409` if the scene is finished.

### POST /api/stories/{story_id}/scenes/{scene_id}/finish

Finish a scene and persist its summary.

**Request**

```json
{
    "scene_summary": ["The hero discovered the map.", "He escaped the harbor."]
}
```

`scene_summary` must contain 1–100 non-empty strings.

**Response 200**

```json
{
    "data": {
        "id": 3,
        "finished": true,
        "scene_summary": ["The hero discovered the map.", "He escaped the harbor."]
    }
}
```

**Responses**: `404` for a missing story or scene; `409` if the scene is already finished; `422` for an invalid summary.

## Choice-Driven Story Endpoints

### GET /api/stories/{story_id}/choice-play

Return a choice-driven story and its ordered steps.

**Response 200**

```json
{
    "data": {
        "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        "title": "The Black Harbor",
        "steps": [
            {
                "id": 1,
                "incoming_choice": null,
                "text": "The ship enters the harbor.",
                "choices": [{"action": "Dock", "consequence": "The crew is noticed."}]
            }
        ]
    }
}
```

**Response 404**: story not found.

### POST /api/stories/{story_id}/choice-play/generate-choices

Generate choices for the latest step.

**Response 200**

```json
{"data": {"choices": [{"action": "Dock", "consequence": "The crew is noticed."}]}}
```

**Responses**: `404` if the story or required character is missing; `409` if the story has no steps; `502` if an LLM request fails.

### POST /api/stories/{story_id}/choice-play/regenerate-choices

Clear and regenerate choices for the latest step. The response shape is the same as `generate-choices`.

**Responses**: `404` if the story or required character is missing; `409` if the story has no steps; `502` if an LLM request fails.

### POST /api/stories/{story_id}/choice-play/select-choice

Select a choice and generate the next story step.

**Request**

```json
{"action": "Dock", "consequence": "The crew is noticed."}
```

**Response 200**

```json
{
    "data": {
        "id": 2,
        "incoming_choice": {"action": "Dock", "consequence": "The crew is noticed."},
        "text": "A harbor guard approaches the ship.",
        "choices": []
    }
}
```

**Responses**: `404` if the story or required character is missing; `502` if an LLM request fails.

### PATCH /api/stories/{story_id}/choice-play/steps/{step_id}

Update a step's text.

**Request**

```json
{"text": "The ship slips quietly into the harbor."}
```

`text` must contain 1–4000 characters.

**Response 200**

```json
{"data": {"id": 1, "text": "The ship slips quietly into the harbor."}}
```

**Responses**: `404` if the story or step is missing; `422` for invalid text.

### DELETE /api/stories/{story_id}/choice-play/steps/{step_id}/forward

Truncate story history to steps whose IDs are less than or equal to `step_id`.

**Response 200**

```json
{"data": {"step_id": 1}}
```

**Response 404**: story not found.

## Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful read or operation. |
| 201 | Scene created. |
| 404 | Resource not found. |
| 409 | Domain rule prevents the operation. |
| 422 | Request validation failed or selected model is unavailable. |
| 500 | Unexpected server-side or configuration error. |
| 502 | Upstream LLM request failed. |
