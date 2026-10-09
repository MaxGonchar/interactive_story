# Character-Driven Story API

**Status**: Draft  
**Date**: 2026-10-07

## API Boundaries

- Story and character definitions remain manually prepared. There is no story-creation or character-editing endpoint in this feature.
- Existing shared endpoints remain in use for story listing/detail, story character listing, and model listing. Story responses identify this mode with `type: "character_driven"`.
- Character-driven scene content uses a separate route family under `/api/stories/{story_id}/character-play/`. Existing `/scenes` and `/choice-play` contracts remain unchanged.
- Requests and responses use JSON. Errors use the common `{ "error": { "code": "...", "message": "..." } }` shape.

## Shared APIs

Reuse the existing endpoints:

- `GET /api/stories` and `GET /api/stories/{story_id}` for story metadata and scene references.
- `GET /api/stories/{story_id}/characters` for character IDs and names.
- `GET /api/models` for configured models and the default model ID.

The story type union adds `character_driven`. `GET /api/stories/{story_id}` also returns `type` (an additive field), so the frontend can choose its scene routes. Story creation remains out of scope; users add the story YAML and character files manually.

## Character-Driven Scene Endpoints

### Create a scene

`POST /api/stories/{story_id}/character-play/scenes`

Creates the next scene. Reject creation if another scene is active. The player character may be `null`; the UI presents this option as the `Narrator` pseudo-role. That is still a player turn, not a narrator-agent turn.

**Request**

```json
{
	"user_character_id": null,
	"character_ids": ["navigator", "harbor_guard"],
	"context": ["The ship has reached the harbor."],
	"general_scene_guide": "Keep tension rising.",
	"writing_style": "Cinematic and concise.",
	"first_message": "A bell rings through the fog.",
	"character_model_id": "character-model",
	"narrator_model_id": "narrator-model"
}
```

Both model IDs are required and must refer to configured models. The UI initially selects the registry default for each. For later scenes, it derives each model selection from the prior finished scene's items and their `llm_data`, falling back to the registry default if the derived model is no longer configured. The selected IDs are stored in the opening item's `llm_data` and become the scene's initial model defaults.

`user_character_id` is required but nullable. `character_ids` defaults to an empty list. The player character cannot also appear in `character_ids`; all non-null character IDs must belong to the story. Duplicate IDs in `character_ids` are rejected. `context` must contain at least one non-empty item, and `general_scene_guide`, `writing_style` and `first_message` must be non-empty. `first_message` is at most 4000 characters. The scene starts with the supplied opening narration as its first story item, and that item's `llm_data` stores the two model IDs selected at creation.

**Response 201**

```json
{"data": {"id": 1, "finished": false}}
```

**Errors**: `404 not_found` for a missing story or character; `409 active_scene_exists` if a scene is already active; `422 validation_error` for invalid fields or model IDs.

### Get a scene

`GET /api/stories/{story_id}/character-play/scenes/{scene_id}`

Returns scene configuration, participant IDs, status, summary, context, and all story items in order. A story item contains its actor/input, generated character action when applicable, narrator paragraph, and model metadata. The UI displays the narration by default but receives the full stored item. Model selections for later scenes can be derived from the items' `llm_data`; model selection is not returned as a separate scene-level field.

**Response 200**

```json
{
	"data": {
		"id": 1,
		"finished": false,
		"user_character_id": null,
		"character_ids": ["navigator", "harbor_guard"],
		"scene_description": {
			"general_scene_guide": "Keep tension rising.",
			"writing_style": "Cinematic and concise."
		},
		"context": ["The ship has reached the harbor."],
		"scene_summary": null,
		"items": [
			{
				"id": 1,
				"actor": null,
				"input": null,
				"character_action": null,
				"narration": "A bell rings through the fog.",
				"llm_data": {
					"character_model_id": "character-model",
					"narrator_model_id": "narrator-model"
				}
			},
			{
				"id": 2,
				"actor": {"type": "character", "character_id": "navigator"},
				"input": {"guidance": "Warn the captain about the harbor master."},
				"character_action": "The navigator leans close and warns the captain.",
				"narration": "The navigator catches the captain's sleeve and whispers a warning.",
				"llm_data": {
					"character_model_id": "character-model",
					"narrator_model_id": "narrator-model"
				}
			}
		]
	}
}
```

For a player item, `actor` is `{ "type": "player" }`, `input.action` contains the player's action, and `character_action` is `null`. When `user_character_id` is null, the player's author has no character ID; the API still identifies the actor as `player`. For a character item, `input.guidance` is optional and `character_action` contains the generated action. The opening item has no actor or input; its `llm_data` records the model selections made at scene creation. For later items, `llm_data` records the models used for the turn, so the character model is `null` for player turns.

For the next scene's form, derive each model independently from the most recent item that used that model. A player item has `character_model_id: null`, so it does not replace the last character model used. The opening item carries the creation-time selections, so both models are always derivable. If a derived ID is no longer in the model registry, use the registry default. The scene-detail response does not include scene-level model defaults or computed last-used model fields.

**Errors**: `404 not_found` if the story or scene does not exist.

### Submit a turn

`POST /api/stories/{story_id}/character-play/scenes/{scene_id}/turns`

Processes a player or character turn synchronously. The server calls the narrator for a player turn, or calls the selected character agent followed by the narrator for a character turn. Persist one complete item only after every required LLM call succeeds. If any call fails, persist no item; the UI keeps its form values and can retry the whole request.

**Player request**

```json
{
	"actor": {"type": "player"},
	"action": "I look for the nearest light source.",
	"character_model_id": "character-model",
	"narrator_model_id": "narrator-model"
}
```

**Character request**

```json
{
	"actor": {"type": "character", "character_id": "navigator"},
	"guidance": "Warn the captain about the harbor master.",
	"character_model_id": "character-model",
	"narrator_model_id": "narrator-model"
}
```

For a player actor, `action` is required and `guidance` is not accepted. For a character actor, `guidance` is optional; an omitted or empty value asks the character to react to the current scene. `character_model_id` and `narrator_model_id` are required in both requests. The character ID must be among the scene's `character_ids`. Player actors use the scene's `user_character_id`, which may be null. Both model IDs are validated against the registry for every turn, including player turns, which store `character_model_id: null`. The new item's ID is the current maximum item ID plus one.

**Response 200** returns the newly saved full item, using the same item shape as scene detail. For a player turn, `input.action` stores the player action. For a character turn, `input.guidance` stores the optional guidance and `character_action` stores the generated contribution.

**Errors**: `404 not_found` for a missing story, scene, or character; `409 scene_finished` if the scene is finished; `422 validation_error` for invalid input, an unselected character, or unavailable model; `502 llm_error` if a model call fails. The UI receives the general LLM error message; logs identify whether character generation or narration failed.

### Edit a story item

`PUT /api/stories/{story_id}/character-play/scenes/{scene_id}/items/{item_id}`

Updates only the narrator paragraph. Actor, input, generated character action, item ID, and position do not change. Any item, including the opening item, can be edited. `narration` must be 1-4000 characters.

**Request**

```json
{"narration": "The captain turns toward a wavering light."}
```

**Response 200** returns the updated full item. **Errors**: `404 not_found`; `409 scene_finished`; `422 validation_error` for invalid narration.

### Delete the last story item

`DELETE /api/stories/{story_id}/character-play/scenes/{scene_id}/items/{item_id}`

Deletes only the current last item. IDs of remaining items are not renumbered, and the next created item uses the maximum remaining ID plus one, so a deleted ID can be reused. The opening item cannot be deleted.

**Response 200**

```json
{"success": true}
```

**Errors**: `404 not_found`; `409 scene_finished`; `409 not_last_item` if the item is not the latest item; `409 opening_item_not_deletable` for the opening item.

### Replace the last turn

`POST /api/stories/{story_id}/character-play/scenes/{scene_id}/turns/{item_id}/replace`

Uses the same player or character request body as turn submission. Only the latest turn can be replaced. The existing item remains intact unless all LLM calls succeed; on success, replace it in place without changing its ID. The UI restores its actor and input, allows edits, and resubmits both required model IDs. A failure leaves the existing item unchanged and returns the general LLM error.

**Errors**: `404 not_found`; `409 scene_finished`; `409 not_last_item` if the item is not latest; `409 not_replaceable` if the item has no turn input; `422 validation_error`; `502 llm_error`.

### Generate a summary draft

`GET /api/stories/{story_id}/character-play/scenes/{scene_id}/summary/draft`

Generates and returns a summary for review. This does not save or finish the scene. Each request generates a fresh draft using the configured `SUMMARY_MODEL`; the request takes no model ID. Return `Cache-Control: no-store`; clients call this endpoint only on explicit user action.

**Response 200**

```json
{"data": {"summary": ["The crew uncovered a betrayal."]}}
```

**Errors**: `404 not_found`; `409 scene_finished`; `502 llm_error`.

### Generate a character memory draft

`GET /api/stories/{story_id}/character-play/scenes/{scene_id}/characters/{character_id}/memory/draft`

Generates new memory entries for one participating character, including the player character. Does not save the entries or update the character file. Each request generates a fresh draft using the configured `SUMMARY_MODEL`; the request takes no model ID. Return `Cache-Control: no-store`.

**Response 200**

```json
{
	"data": {
		"character_id": "navigator",
		"memory_updates": ["The captain trusted the navigator's warning."]
	}
}
```

An empty `memory_updates` list is valid. **Errors**: `404 not_found` for a missing story, scene, or character; `409 scene_finished` or `409 character_not_in_scene`; `502 llm_error`.

### Finish a scene

`POST /api/stories/{story_id}/character-play/scenes/{scene_id}/finish`

Stores the reviewed summary and all reviewed character-memory updates, then marks the scene finished. This is the only operation that saves generated/reviewed finish outputs. Memory updates are appended to each character's existing memory; entries already present in a character's memory are skipped. `scene_summary` must contain 1-100 non-empty items.

**Request**

```json
{
	"scene_summary": ["The crew uncovered a betrayal."],
	"character_memory_updates": {
		"captain": ["The navigator warned her about the harbor master."],
		"navigator": []
	}
}
```

`character_memory_updates` must contain exactly one entry for every character participating in the scene, including the player character when one is assigned. Empty lists mean no new memories. The server validates all IDs and values before writing.

**Response 200**

```json
{
	"data": {
		"id": 1,
		"finished": true,
		"scene_summary": ["The crew uncovered a betrayal."],
		"character_memory_updates": {
			"captain": ["The navigator warned her about the harbor master."],
			"navigator": []
		}
	}
}
```

**Errors**: `404 not_found`; `409 scene_finished`; `422 validation_error` for invalid summary or a memory-update map that does not match the scene participants.

## Error and Persistence Guarantees

- LLM failures return `502` with the general `llm_error` message. Structured server logs include the failed operation stage; the stage is not exposed in the UI response.
- Turn submission and replacement are all-or-nothing with respect to the scene item: failed chains do not append or replace items. A retry re-runs the whole request, so a retried character action may differ from the failed attempt.
- LLM usage records for a turn are written only after the item is persisted. Failed chains record no usage.
- Summary and memory draft GETs do not modify story or character data. LLM usage logging may record the calls.
- The finish endpoint is one API operation, but scene metadata and multiple character memories are stored in separate YAML files, and per-file atomic writes do not make that a transaction. The implementation validates everything first, writes each character's memory, and writes the scene metadata (the `finished` flag) last. If a write raises an error, it restores the previous memories and re-raises, so an error leaves persisted data unchanged. A hard process crash mid-finish can leave some memories appended with the scene still unfinished; a retry is safe because entries already present are skipped. There is no write-ahead journal.

## Resolved API Decisions

- The opening narration item cannot be deleted (`409 opening_item_not_deletable`). It can be edited.
- Finish consistency uses validate-first ordered writes with rollback on errors, as described under Error and Persistence Guarantees.
- Finish-time summary and memory generation use the configured `SUMMARY_MODEL`; the draft requests take no model ID.
