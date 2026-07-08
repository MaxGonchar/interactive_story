# API Contract (MVP)

## Overview

Base path: `/api`
Content-Type: `application/json`

## Standard Error Response

All 4xx and 5xx responses use this shape:

```json
{
    "error": {
        "code": "string",
        "message": "string"
    }
}
```

Common error codes:
- `not_found` – requested resource does not exist
- `validation_error` – request body or path parameter failed validation
- `scene_finished` – operation rejected because scene is already finished
- `llm_error` – LLM call failed; scene history was not modified
- `internal_error` – unexpected server-side failure

---

## Endpoints

### GET /api/stories

List all stories.

**Response 200**
```json
{
    "data": [
        {
            "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
            "title": "The Black Harbor"
        }
    ]
}
```

Stories are ordered by their `order` field ascending.

---

### GET /api/stories/{story_id}

Get story metadata and its scene list.

**Path parameters**
- `story_id`: UUID string

**Response 200**
```json
{
    "data": {
        "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        "title": "The Black Harbor",
        "scenes": [
            {
                "id": 1,
                "finished": true
            },
            {
                "id": 2,
                "finished": true
            },
            {
                "id": 3,
                "finished": false
            }
        ],
        "active_scene_id": 3
    }
}
```

Scenes are ordered by their `order` field ascending.

**Response 404** – story not found

---

### GET /api/stories/{story_id}/scenes/{scene_id}

Get scene content: metadata and full message history.

**Path parameters**
- `story_id`: UUID string
- `scene_id`: integer

**Response 200**
```json
{
    "data": {
        "id": 3,
        "finished": false,
        "scene_description": {
            "general_scene_guide": "Keep tension rising with small discoveries and choices.",
            "writing_style": "Cinematic, sensory details, concise dialog turns."
        },
        "scene_summary": null,
        "messages": [
            {
                "id": 1,
                "role": "assistant",
                "content": "You step into the foggy harbor..."
            },
            {
                "id": 2,
                "role": "user",
                "content": "I look for the nearest light source."
            }
        ]
    }
}
```

`scene_summary` is `null` when scene is not finished, and a non-empty list of strings when finished.
Messages are ordered by `id` ascending.

**Response 404** – story or scene not found

---

### POST /api/stories/{story_id}/scenes/{scene_id}/play

Send a user message and receive the assistant response.

This is the core scene-playing operation. The server:
1. Validates scene is not finished.
2. Calls the LLM with scene context (characters, description, message history, new user message).
3. On LLM success: persists user message and assistant message atomically.
4. Returns both messages.

If the LLM call fails, **neither** message is persisted. The scene history remains unchanged.

**Path parameters**
- `story_id`: UUID string
- `scene_id`: integer

**Request**
```json
{
    "content": "I look for the nearest light source."
}
```

Validation:
- `content`: required, non-empty string, max 4000 characters

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
            "content": "A lantern swings near a wooden post..."
        }
    }
}
```

Both messages are returned so the client can append them to the chat in the correct order without a full page reload.

**Response 404** – story or scene not found
**Response 422** – validation error (content missing or too long)
**Response 409** – scene is already finished (`scene_finished` error code)
**Response 502** – LLM call failed (`llm_error` error code); scene unchanged

---

### PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}

Edit an existing message in the current scene.

This endpoint is included in MVP because message correction is part of the current scene-playing workflow and is required for equivalent user experience.

**Path parameters**
- `story_id`: UUID string
- `scene_id`: integer
- `message_id`: integer

**Request**
```json
{
    "content": "I carefully inspect the lantern and the alley behind it."
}
```

Validation:
- `content`: required, non-empty string, max 4000 characters

**Response 200**
```json
{
    "data": {
        "id": 2,
        "role": "user",
        "content": "I carefully inspect the lantern and the alley behind it."
    }
}
```

Rules:
- message must exist in the scene
- editing is allowed only while scene is not finished
- role is immutable; only `content` can change
- ids of other messages do not change

**Response 404** – story, scene, or message not found
**Response 422** – validation error (content missing or too long)
**Response 409** – scene is already finished (`scene_finished` error code)

---

### DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}

Delete an existing message from the current scene.

This endpoint is included in MVP because message deletion is part of the current scene-playing workflow and is required for equivalent user experience.

**Path parameters**
- `story_id`: UUID string
- `scene_id`: integer
- `message_id`: integer

**Response 200**
```json
{
    "success": true
}
```

Rules:
- message must exist in the scene
- deletion is allowed only while scene is not finished
- remaining message ids are preserved; ids are not re-numbered

**Response 404** – story, scene, or message not found
**Response 409** – scene is already finished (`scene_finished` error code)

---

### POST /api/stories/{story_id}/scenes/{scene_id}/finish

Mark the scene as finished and record its summary.

**Path parameters**
- `story_id`: UUID string
- `scene_id`: integer

**Request**
```json
{
    "scene_summary": ["The hero discovered the map.", "He escaped the harbor."]
}
```

Validation:
- `scene_summary`: required list of 1–100 non-empty strings

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

Calling finish on an already-finished scene returns 409 with `scene_finished` error code.

**Response 404** – story or scene not found
**Response 422** – validation error (summary missing or too long)
**Response 409** – scene is already finished

---

## Post-MVP Endpoints (out of scope for MVP)

The following endpoint from the original draft is deferred to post-MVP:

- `PATCH /stories/{story_id}/scenes/{scene_id}` – general scene metadata update

---

## Status Code Summary

| Code | Meaning |
|------|---------|
| 200  | Success |
| 404  | Resource not found |
| 409  | Conflict (e.g. scene already finished) |
| 422  | Validation error |
| 502  | Upstream LLM failure |
| 500  | Internal server error |
