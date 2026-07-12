# Feature: Scene Summary Generation

**Status**: Draft  
**Date**: 2026-07-12

## Summary
When a user finishes a scene, the app opens a modal requiring a scene summary. This feature adds a "Generate Summary" button to that modal which calls an AI service to produce a bullet-point summary automatically. The user can review, edit, and then submit the generated text — reducing friction at the end of every scene.

## Value
- Eliminates the most tedious manual step in the scene-finishing flow.
- Keeps narrative continuity by feeding the scene's accumulated context (`context` field) to the LLM alongside the current scene's messages.
- Success criteria: user can finish a scene with a generated summary in fewer steps and less time than typing one manually.

## Scope

### In scope for first iteration
- "Generate Summary" button in `FinishModal`.
- `GET /api/stories/{story_id}/scenes/{scene_id}/summarize` endpoint.
- LLM prompt using Jinja templates (system prompt + user message template).
- New env variable for the summary model name.
- Modal locked during generation; on error — show message and re-enable the form.
- Backend tests for the new endpoint and LLM client.

### Out of scope / future
- Auto-triggering generation on modal open.
- Streaming the generated summary token by token.
- Saving a draft summary before the user submits.
- Configuring prompt behaviour from the UI.

## User Flow
1. User clicks "Finish Scene" — `FinishModal` opens.
2. User clicks "Generate Summary".
3. Modal is fully disabled (textarea + all buttons) and shows a loading state.
4. Frontend calls `GET /api/stories/{story_id}/scenes/{scene_id}/summarize`.
5. **On success**: generated bullet-list text is injected into the textarea; modal re-enables.
6. **On error**: error message is displayed; modal re-enables so the user can retry or type manually.
7. User optionally edits the text, then clicks "Finish" to submit.


## API Changes

### New endpoint

**`GET /api/stories/{story_id}/scenes/{scene_id}/summarize`**

Generates a bullet-point summary of the scene using an LLM. No request body. All input data is assembled on the backend from storage.

**Path parameters**
- `story_id`: UUID string
- `scene_id`: integer

**Response 200**
```json
{
    "data": {
        "summary": ["Item one", "Item two", "Item three"]
    }
}
```

The `summary` value is a list of strings. Formatting into the bullet-list textarea format is the UI's responsibility.

**Error responses**
- `404` — story or scene not found
- `409` / `scene_finished` — scene is already finished
- `500` / `llm_error` — LLM call failed; no state is modified

---

## Data Changes

No changes to the YAML storage format. The endpoint reads existing fields:
- `metadata.yaml` → `context` field (list of strings) as the previous summary input.
- `messages.yaml` → full message list as the new chapter text input.

---

## Backend Changes

### New: `SummarizeLLMClient` (in `backend/app/llm/`)
- Accepts scene context (up to last 50 items) and scene messages.
- Renders system prompt and user message via Jinja2 templates.
- Calls LLM via LangChain using a model name read from a new env variable (`SUMMARY_MODEL`).
- Uses a LangChain structured output parser (e.g. `PydanticOutputParser` or tool-calling) to enforce a `list[str]` response shape — eliminating reliance on the LLM producing well-formed bullet text.
- Returns `list[str]`.

### New: `SceneSummarizeService` (in `backend/app/services/`)
- Loads scene metadata and messages via existing repositories.
- Assembles `previous_summary` from the last ≤50 items of `metadata.context`.
- Assembles `scene_content` by concatenating messages as `{role}:\n{content}` blocks.
- Delegates to `SummarizeLLMClient` and returns the result.

### New router handler
- `GET /api/stories/{story_id}/scenes/{scene_id}/summarize`
- Injects `SceneSummarizeService` via dependency injection.
- Returns `{"data": {"summary": "..."}}`.

### New env variable
```
SUMMARY_MODEL=<model-name>
```

---

## Frontend Changes

### `FinishModal.jsx`
- Accept two new props: `storyId` and `sceneId`.
- Add "Generate Summary" button.
- On click: call the new API endpoint, lock the entire modal (textarea + all buttons) with a loading indicator.
- On success: convert the returned `summary` list to bullet text (`- item\n- item\n...`) and populate the textarea; unlock the modal.
- On error: display an inline error message; unlock the modal so the user can retry or type manually.
- Increase modal width by ~20% and height by ~40% to give the textarea more room.

### `ScenePage.jsx`
- Pass `storyId` and `sceneId` (already available via `useParams()`) as props to `FinishModal`.

### `frontend/src/api/scenes.js`
- Add `generateSceneSummary(storyId, sceneId)` function calling the new endpoint.

---

## Prompts

### System prompt (`summary_system.j2`)
```
You are a specialized narrative assistant. Your task is to generate a chronological list of bullet points summarizing story chapters provided by the user. The user will provide the text of a new chapter and, if applicable, a summary of previous chapters. You must ensure the new summary is consistent with the provided context.

Core Rules:
1. Output Format: Return a bulleted list only. Do not include introductions, conclusions, or meta-commentary.
2. Chronology: List events in the order they occur in the text.
3. Attribution: Ensure every bullet point clearly identifies who performed the action or spoke the dialogue. Use active voice (e.g., "Max says...", "Lyra walks...").
4. Completeness: Do not skip any events, including explicit sexual content or violence. Maintain the tone of the original story—be concise but descriptive.
5. Context Integration: If a previous summary is provided, use it to maintain narrative consistency. Do not contradict established facts.
6. Detail Level: Provide a short version of what happened, capturing key actions and dialogue without unnecessary fluff.

Process:
- Read the provided chapter text and previous summary (if any).
- Extract key events, dialogue, and interactions.
- Format them into a clear, bulleted list ensuring clear subject attribution.
- Verify that the tone matches the source material and no content is censored.
```

### User message prompt (`summary_user.j2`)
```
## Previous summary:
{{ previous_summary }}

## New chapter text:
{{ scene_content }}

Please generate a concise, chronological bulleted summary of the new chapter, ensuring consistency with the previous summary. Each bullet point should clearly identify the subject performing the action or speaking the dialogue. Maintain the tone of the original story, and do not omit any explicit sexual content or violence. Return only the bulleted list without introductions or conclusions.
```

#### `previous_summary` rendering
Last ≤50 items from `metadata.context`, formatted as:
```
- [context item 1]
- [context item 2]
...
```
If `context` is empty, the section is omitted from the prompt.

#### `scene_content` rendering
All messages from `messages.yaml`, concatenated as:
```
{role}:
{content}

{role}:
{content}
```

---

## Open Questions

None at this time.

---

## Risks

- Large scenes with many messages may produce very long prompts — worth monitoring token usage once in use.
