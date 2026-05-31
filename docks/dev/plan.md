# Implementation Plan

## Scope
This plan covers MVP delivery only.
Post-MVP roadmap is listed separately at the bottom.

---

## Milestones

### ✅ M1 — Project Skeleton

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

### ✅ M2 — API Contract Stubs

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

### ✅ M3 — Frontend UI Pages (Mocked)

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

### ✅ M4 — Data Access Layer

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

### ✅ M5 — LLM Adapter

**Goal:** LLM client sends a constructed prompt to the model and returns a text response.
As an LLM service we are going to use venice ai.
Here is example of integration in another project:
https://github.com/MaxGonchar/gameV5/blob/main/backend/app/llm/venice_client.py
https://github.com/MaxGonchar/gameV5/blob/main/backend/app/llm/venice_ai.py

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

### ✅ M6 — Services and Full Integration

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

==================================================================

# Post implementation problems and improvements

## Planed:

----------------------------------------------------------------------------------------------------

### On hover cursor ❌
- UI: stories page: when I hover the story title I can not understand that it is clickable
- UI: scenes page: when I hover the scene id I can not understand that it is clickable

#### Problem Summary

Both `StoryList` and `SceneList` render clickable `<li>` elements with `onClick` handlers, but no CSS is applied to those `<li>` elements to signal interactivity. There is no `cursor: pointer`, no hover color/underline change, and no `user-select` hint. The browser renders them as plain list items, so the user has no visual affordance that they are clickable.

#### Expected Behavior

When a user hovers over a story title (in `StoriesPage`) or a scene row (in `StoryPage`), the cursor should change to a pointer and the item should visually highlight, making it clear the element is interactive.

#### Root Cause

**File**: StoryList.jsx  
**File**: SceneList.jsx

Both components attach `onClick` directly to `<li>` elements but apply zero interactive styling. There are no hover rules for list items anywhere in index.css — the stylesheet has no `li`, `ul li`, or component-specific hover rules at all.

#### Evidence

StoryList.jsx line 8–10:
```jsx
<li key={story.id} onClick={() => onSelect(story.id)}>
  {story.title}
</li>
```

SceneList.jsx line 8–11:
```jsx
<li key={scene.id} onClick={() => onSelect(scene.id)}>
  Scene {scene.id}
  ...
</li>
```

index.css contains no `cursor: pointer` or hover rule for `li` elements. There are no scoped CSS modules or component-level stylesheets.

#### Fix Plan

1. **File: index.css** — Add a global hover rule for interactive list items (or a utility class, e.g. `.clickable`):
   - Set `cursor: pointer` on hover
   - Change text color to `var(--accent)` (or `var(--text-h)`) on hover
   - Optionally add a subtle `background` highlight using `var(--accent-bg)`
   - **Why**: the `<li>` elements are the only clickable list items in the app; a global `li[onClick]` selector or a shared class solves both cases at once.

   Alternatively (cleaner and more explicit):

2. **File: StoryList.jsx** — Add an `style` prop or `className` (e.g. `"clickable"`) to the `<li>`.

3. **File: SceneList.jsx** — Same: add `style` prop or the same `className` to the `<li>`.

The simplest safe approach: add a `.clickable` rule to index.css and apply `className="clickable"` in both components.

#### Test Coverage Gaps

- No frontend tests exist for these components. A visual regression / Storybook story would prevent this class of affordance regression, but is out of MVP scope.

#### Risks / Edge Cases

- If a scene is `finished` you may want a different cursor or a muted color to hint it is navigable but no longer active — not required now, but worth considering when the hover style is chosen.
- Avoid styling bare `li` globally since other `<ul>/<li>` usages (e.g. inside `MessageList`) may not be clickable.

----------------------------------------------------------------------------------------------------

### Extra scene description ❌
- UI: scene page: entry point should be a first assistant message but not the description

#### Problem Summary

The scene page shows the `entry_point` text from `scene_description` as a static plain-text description paragraph in `SceneHeader`, while the same text is also stored as message id=1 (`role: assistant`) in messages.yaml and rendered again as a chat bubble by `MessageList`. The entry point text appears twice: once as a raw description and once as a proper assistant message. The user wants it to appear only as a first assistant message — not as a header description.

---

#### Expected Behavior

The scene page's entry point should appear only as the first assistant message in the chat message list (rendered via `MessageList`/`MessageItem` as a chat bubble). The `SceneHeader` should show only the scene ID and status, with no description paragraph.

This aligns with the domain definition in requirements.md: *"Scene Description: structured scene context with entry point, guide, and writing style"* — the scene description is internal LLM context, not a UI display element.

---

#### Root Cause

**File**: SceneHeader.jsx  
**Line 7**: `<p>{scene.scene_description.entry_point}</p>`

`SceneHeader` renders the `entry_point` field as a static description paragraph. The same text is already stored as the first assistant message in messages.yaml (e.g. message id=1, role=assistant), so `MessageList` also renders it as a chat bubble. The entry point text is displayed twice.

---

#### Evidence

data/stories/a9b18181.../scenes/1/meta.yaml — `entry_point` value:
> "Middle of the day. Seclude part of the huge park..."

data/stories/a9b18181.../scenes/1/messages.yaml — message id=1, role=assistant, content:
> "Middle of the day. Seclude part of the huge park..."

These are identical strings. `SceneHeader` renders the former as a `<p>` tag; `MessageList` renders the latter as a chat bubble — the user sees the entry point paragraph and then the same text again as the first message bubble.

---

#### Fix Plan

1. **File: SceneHeader.jsx** — Remove the `<p>{scene.scene_description.entry_point}</p>` line (line 7). The header should only render the scene ID and status badge. **Why**: the entry_point is already stored as the first assistant message; `MessageList` will display it naturally as a chat bubble.

2. **No backend changes needed.** The API correctly returns both `scene_description` (for LLM context) and `messages` (for display). The API contract should remain unchanged.

---

#### Test Coverage Gaps

- No frontend component tests exist. A test verifying that `SceneHeader` does **not** render `scene_description.entry_point` as text content would prevent this class of regression. Similarly, a test checking that the first rendered `MessageItem` is the entry_point assistant message would cover the expected display path.

---

#### Risks / Edge Cases

- **Edge case — scene with zero messages**: If a manually-prepared scene has no messages yet (unlikely but possible), removing the description paragraph means the user sees "No messages yet." with no narrative context. Mitigation: ensure all scenes are seeded with at least the entry_point as the first assistant message before the app reads them (a data preparation convention, not a code change).
- **`scene_description` prop on `SceneHeader`**: After the fix, `scene_description` is no longer consumed by `SceneHeader`. If `SceneHeader` stops accepting `scene` entirely and only takes `{id, finished}`, that is a nice cleanup — but strictly optional and out of scope for this fix.


----------------------------------------------------------------------------------------------------


### Absent env configs for LLM adapter ❌
- No env configs for LLM adapter (model name, API key, etc.)

#### Problem Summary

.env.example does not contain entries for `VENICE_API_KEY` or `VENICE_MODEL`. These are the two environment variables required by `SceneLLMClient` (M5 deliverable). Any developer who copies .env.example → `.env` will have a `.env` file missing these keys. The server boots fine, but the first call to `POST /play` crashes with an unhandled `KeyError: 'VENICE_API_KEY'`.

#### Expected Behavior

Per plan.md M1 and M5:
- .env.example must document **all** required environment variables with description comments.
- `VENICE_API_KEY` (required) and `VENICE_MODEL` (optional, defaults to `llama-3.3-70b`) must be listed.

#### Root Cause

**File**: .env.example, all lines

.env.example was authored during M1 before the LLM adapter (`VENICE_API_KEY`, `VENICE_MODEL`) was specified in M5. It was never updated after M5 was completed. The two LLM-specific env vars are entirely absent.

**File**: scene_llm_client.py

```python
api_key = os.environ["VENICE_API_KEY"]          # line 14 — hard KeyError if missing
model   = os.environ.get("VENICE_MODEL", ...)   # line 15 — safe, has default
```

`VENICE_API_KEY` uses `os.environ[...]` (direct key access), so a missing key raises `KeyError` at request time, not at startup. This makes the failure late and opaque.

#### Evidence

- `grep` confirms `VENICE_API_KEY` / `VENICE_MODEL` only appear in scene_llm_client.py, its test, and a DONE task doc — never in .env.example.
- `get_scene_llm_client()` in dependencies.py constructs `SceneLLMClient()` per-request (not at startup), so the `KeyError` is deferred until the first `/play` call.
- main.py calls `load_dotenv()` at module level, so a properly-populated `.env` would work — the gap is purely in documentation/template.

#### Fix Plan

1. **File: .env.example** — Add `VENICE_API_KEY` and `VENICE_MODEL` entries with descriptive comments. `VENICE_API_KEY` should be marked as required (no default). `VENICE_MODEL` should document the default (`llama-3.3-70b`) and note it is optional.

2. **File: main.py** — After `load_dotenv()`, add a startup check that raises a clear `RuntimeError` (or uses a FastAPI `lifespan` startup event) if `VENICE_API_KEY` is not set in the environment. This converts the silent late `KeyError` into an explicit fast-fail at app startup. Example:
   ```python
   if not os.getenv("VENICE_API_KEY"):
       raise RuntimeError("VENICE_API_KEY environment variable is required but not set.")
   ```

#### Test Coverage Gaps

- No test verifies that `SceneLLMClient()` raises a meaningful error when `VENICE_API_KEY` is absent (the `autouse` fixture always sets it). A test with `monkeypatch.delenv("VENICE_API_KEY")` should confirm the exact exception type/message.
- No integration or startup test catches a missing env var at app boot time (if step 2 is implemented).

#### Risks / Edge Cases

- If the startup validation in main.py is added, it will break any CI environment that imports or starts the app without `VENICE_API_KEY` set. Those environments must either set a dummy key or the check must be guarded (e.g., only in non-test mode).
- `VENICE_MODEL` is already safe (`os.environ.get` with a default) — no change needed to that line, only documentation. Problem Summary

.env.example does not contain entries for `VENICE_API_KEY` or `VENICE_MODEL`. These are the two environment variables required by `SceneLLMClient` (M5 deliverable). Any developer who copies .env.example → `.env` will have a `.env` file missing these keys. The server boots fine, but the first call to `POST /play` crashes with an unhandled `KeyError: 'VENICE_API_KEY'`.

----------------------------------------------------------------------------------------------------

### Not working "Send" and "Finish" buttons on scene page ❌
- UI: scene page: no call to BE when I press "Send" btn. The same for "finish" btn.

#### Problem Summary

When the user presses **Send** or **Finish Scene** on the scene page, no HTTP requests are sent to the backend. Both buttons visually respond (e.g., the composer clears) but the API is never called. This is a holdover from the M3 mocked phase that was never replaced during M6 integration.

---

#### Expected Behavior

Per plan.md M6 and endpoints.md:
- **Send** → `POST /api/stories/{story_id}/scenes/{scene_id}/play` with `{ content }`, appending the returned `user_message` and `assistant_message` to the message list.
- **Finish** → `POST /api/stories/{story_id}/scenes/{scene_id}/finish` with `{ scene_summary }`, updating the scene to `finished: true` and displaying the summary.

---

#### Root Cause

**File**: ScenePage.jsx

Both handlers passed down to child components are console-log stubs left from M3:

```jsx
// Line 36
<MessageComposer
  onSend={() => console.log('send')}   // ← stub, never calls playScene()
  disabled={scene.finished}
/>
// Line 41
<SceneActions
  finished={scene.finished}
  sceneSummary={scene.scene_summary}
  onFinish={() => console.log('finish')} // ← stub, never calls finishScene()
/>
```

Neither `playScene` nor `finishScene` is imported in ScenePage.jsx. The child components (`MessageComposer`, `SceneActions`) are correctly implemented — they call `onSend(trimmed)` and `onFinish()` respectively; the fault is entirely in ScenePage.jsx.

**Secondary root cause** — `SceneActions` has no input for `scene_summary`:

`POST /finish` requires a non-empty `scene_summary` string. `SceneActions` currently calls `onFinish()` with no arguments, so there is no way for `ScenePage` to receive a summary even if it tried. The `sceneSummary` prop it already accepts is the read-only display value for an already-finished scene, not a write input.

---

#### Evidence

ScenePage.jsx: handlers are stubs.

scenes.js: `playScene` and `finishScene` are fully implemented but never imported by ScenePage.jsx.

MessageComposer.jsx: `handleSend` correctly calls `onSend(trimmed)` — the component is correct.

SceneActions.jsx: calls `onFinish()` with no arguments — no summary is passed up.

---

#### Fix Plan

1. **File: ScenePage.jsx**
   - Import `playScene` and `finishScene` from `../api/scenes`.
   - Add loading/error state for in-flight operations (optional but recommended).
   - Replace `onSend={() => console.log('send')}` with a real handler that calls `playScene(storyId, sceneId, content)`, then appends `response.data.user_message` and `response.data.assistant_message` to `scene.messages` in state.
   - Replace `onFinish={() => console.log('finish')}` with a real handler that accepts a `summary` argument, calls `finishScene(storyId, sceneId, summary)`, then updates `scene.finished` and `scene.scene_summary` in state from the response.
   - **Why**: these are the only two places the real API calls must originate; the API client and child components are already correct.

2. **File: SceneActions.jsx**
   - Add an internal `useState` for the summary text (a `<textarea>` or `<input>`).
   - Change `<button onClick={onFinish}>` to call `onFinish(summaryText)` only when the input is non-empty.
   - **Why**: `POST /finish` requires a non-empty `scene_summary`; without this change `ScenePage` can never obtain the value even after step 1 is implemented.

3. **File: ScenePage.jsx** *(update after step 2)*
   - Update the `onFinish` prop signature to `onFinish={(summary) => finishScene(storyId, sceneId, summary).then(...)}`.

---

#### Test Coverage Gaps

- No frontend tests exist for `ScenePage`. Tests should verify:
  - Clicking Send calls `playScene` with the correct `storyId`, `sceneId`, and message content.
  - The returned messages are appended to the rendered list.
  - Clicking Finish (with a summary) calls `finishScene` and the page transitions to finished state.

---

#### Risks / Edge Cases

- **Optimistic vs. server-confirmed state**: appending messages before the server confirms creates inconsistency if the LLM call fails (502). The safer approach is to update state only on a successful response and show a loading indicator while the request is in flight.
- **Duplicate sends**: the Send button should be disabled while a play request is in flight to prevent double-submission. `MessageComposer` already accepts a `disabled` prop — `ScenePage` should set it to `true` during the request.
- **`scene_summary` max length**: the API enforces 2000 characters. The `<textarea>` in `SceneActions` should enforce this with `maxLength` or client-side validation before submitting.

----------------------------------------------------------------------------------------------------

### Edit message. ❌
- UI: No icon for "edit" message and no functionality for it. (I want to be able to edit any message in active scene, including assistant messages, to fix typos or add details)

#### Problem Summary

The scene page has no edit affordance on individual messages. `MessageItem` renders a static text bubble with no edit button or icon. There is no inline editing state, no call to `editMessage()` from scenes.js, and no wiring in `ScenePage` to pass an edit handler down to `MessageList` → `MessageItem`. The backend endpoint (`PUT /messages/{message_id}`) and the API client function (`editMessage`) are both fully implemented and correct — only the UI layer is missing.

#### Expected Behavior

Per requirements.md: *"can edit a message in the current active scene"* — any message (user or assistant) in a non-finished scene must be editable. Per endpoints.md, `PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}` accepts `{ content }` and returns the updated message. The UI should show an edit icon on each message (while the scene is active), clicking it should reveal an inline editor pre-filled with the current content, and confirming should call `editMessage()` and update the message in state.

#### Root Cause

The problem spans three components and one page, all missing their edit-related pieces:

**File**: MessageItem.jsx  
Lines 27–34: `MessageItem` accepts only `{ message }`. It has no `onEdit` prop, no edit button/icon, and no editing state. This is the primary display unit — without an edit trigger here the user has no affordance.

**File**: MessageList.jsx  
Lines 9–13: `MessageList` accepts only `{ messages }`. It has no `onEdit` prop and does not pass one to `MessageItem`.

**File**: ScenePage.jsx  
Lines 32–34: `<MessageList messages={scene.messages} />` is called with no `onEdit` prop, and `editMessage` is never imported from `../api/scenes`.

#### Evidence

`editMessage` is fully implemented in scenes.js (lines 23–32) — it calls `PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}`. The backend router at scenes.py lines 95–115 and `SceneMessageService.edit_message` at scene_message_service.py lines 11–21 are complete and correct. The gap is entirely in the frontend component tree.

#### Fix Plan

1. **File: MessageItem.jsx** — Add `onEdit` and `disabled` props. When `disabled` is false (scene active), render an edit icon button on the bubble (visible on hover or always visible). Clicking it switches to an inline edit mode: replace `<p>` with a `<textarea>` pre-filled with `message.content` plus Save/Cancel buttons. On Save call `onEdit(message.id, newContent)`. On Cancel restore original content. **Why**: this is the only place in the render tree where per-message edit actions can live.

2. **File: MessageList.jsx** — Accept `onEdit` and `disabled` props; forward them to each `<MessageItem>`. **Why**: `MessageList` is the intermediary between `ScenePage` and `MessageItem`; the props must pass through.

3. **File: ScenePage.jsx** — Import `editMessage` from `../api/scenes`. Create a handler:
   ```js
   async function handleEditMessage(messageId, content) {
     const res = await editMessage(storyId, sceneId, messageId, content)
     setScene(prev => ({
       ...prev,
       messages: prev.messages.map(m =>
         m.id === messageId ? res.data : m
       )
     }))
   }
   ```
   Pass `onEdit={handleEditMessage}` and `disabled={scene.finished}` to `<MessageList>`. **Why**: `ScenePage` holds the `scene` state and owns `storyId`/`sceneId` from params; it is the correct place for the API call and state update.

4. **File: index.css** — Add hover styles for the edit button (e.g. hide it by default, show on `.message-bubble:hover`), matching the existing CSS variable palette (`--accent`, `--border`, etc.). **Why**: without a hover rule the edit icon will appear on every bubble at all times, cluttering the chat; showing it on hover is the standard pattern.

#### Test Coverage Gaps

- No frontend tests exist for `MessageItem`, `MessageList`, or `ScenePage`. Tests should verify:
  - Edit icon/button is rendered when `disabled={false}` and hidden/absent when `disabled={true}`.
  - Clicking edit switches to inline-edit mode with the correct pre-filled content.
  - Clicking Save calls `onEdit(messageId, newContent)`.
  - Clicking Cancel restores the original content without calling `onEdit`.

#### Risks / Edge Cases

- **In-flight state**: if the user edits a message while a `play` request is in flight, both operations write to messages.yaml simultaneously. The save button should be disabled when any other async operation is running (add a shared `busy` state in `ScenePage`).
- **Concurrent edit conflicts**: two inline edit modes open at once (one per message) are possible if a user opens edit on one bubble and then clicks edit on another. `MessageItem` local state handles this independently; consider closing the first editor when a second opens by lifting the `editingId` state to `MessageList` or `ScenePage`.
- **max 4000 characters**: the inline `<textarea>` should enforce `maxLength={4000}` to match the API validation constraint.
- **Optimistic vs. server-confirmed**: update `scene.messages` only after a successful response from `editMessage()`, not before, to avoid stale content on API error.
- **Role display**: the edit applies to both `user` and `assistant` messages. The edit UX does not need to distinguish between them — both use the same `PUT` endpoint with `content` only.

----------------------------------------------------------------------------------------------------

### Delete message. ❌

- UI: No icon for "delete" message and no functionality for it (I want to be able to delete last user message and following assistant message).

#### Problem Summary

The scene page has no delete affordance on messages. `MessageItem` renders a static text bubble with no delete button or icon. `MessageList` passes no action props to `MessageItem`. `ScenePage` never imports `deleteMessage` from scenes.js and has no handler for paired deletion. The backend `DELETE /messages/{message_id}` endpoint, the service (`SceneMessageService.delete_message`), the repository (`SceneRepository.delete_message`), and the API client function (`deleteMessage` in scenes.js) are all fully implemented and passing all 116 tests — only the UI layer is missing.

---

#### Expected Behavior

Per requirements.md: *"can delete a message in the current active scene"*. The user wants to delete the **last user message and the immediately following assistant message** as a single action (undo last exchange). A delete icon should appear on the last user message bubble when the scene is active. Clicking it should remove both messages and update the message list in state.

---

#### Root Cause

The problem spans three files — all missing their delete-related pieces.

**File**: MessageItem.jsx (lines 1–35)  
`MessageItem` accepts only `{ message }`. No `onDelete` prop, no delete icon button, no conditional render for an action row. This is the primary display unit — without a trigger here the user has no affordance.

**File**: MessageList.jsx (lines 1–16)  
`MessageList` accepts only `{ messages }`. It has no `onDelete` or `disabled` props and does not identify which message is the "last user message eligible for deletion" or pass any action props to `MessageItem`.

**File**: ScenePage.jsx (lines 1–47)  
`deleteMessage` is never imported from `../api/scenes`. No handler exists for deleting a message pair. `<MessageList>` is called with no delete-related props.

---

#### Evidence

`deleteMessage` is fully implemented in scenes.js (lines 35–41) — it calls `DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}`. The backend router at scenes.py (lines 116–139) and `SceneMessageService.delete_message` at scene_message_service.py (lines 22–30) are complete and correct. All 116 backend tests pass, including `test_delete_message_succeeds` and `test_delete_message_raises_when_scene_finished`.

The gap is **entirely in the frontend component tree**.

---

#### Fix Plan

1. **File: MessageItem.jsx** — Add an `onDelete` prop. When `onDelete` is truthy, render a delete icon button (e.g. "✕" or a trash icon) on the message bubble (visible on hover via CSS, or always visible). Clicking it calls `onDelete(message.id)`. **Why**: this is the only place in the render tree where per-message delete actions can live; it is the same pattern being used for the planned edit feature.

2. **File: MessageList.jsx** — Accept `onDelete` and `disabled` props. Compute the **last user message index** in the list: `const lastUserIdx = messages.map(m => m.role).lastIndexOf('user')`. Pass `onDelete` only to the `MessageItem` at `lastUserIdx` (and only when `!disabled`). All other `MessageItem`s receive no `onDelete`. **Why**: delete is scoped to the last exchange only; giving every message a delete button would allow breaking scene history in arbitrary ways the user did not request.

3. **File: ScenePage.jsx** — Import `deleteMessage` from `../api/scenes`. Add a handler:
   ```js
   async function handleDeleteLastExchange(userMessageId) {
     const userIdx = scene.messages.findIndex(m => m.id === userMessageId)
     const assistantMsg = scene.messages[userIdx + 1] // following assistant message
     await deleteMessage(storyId, sceneId, userMessageId)
     if (assistantMsg) {
       await deleteMessage(storyId, sceneId, assistantMsg.id)
     }
     setScene(prev => ({
       ...prev,
       messages: prev.messages.filter(m =>
         m.id !== userMessageId && (!assistantMsg || m.id !== assistantMsg.id)
       )
     }))
   }
   ```
   Pass `onDelete={handleDeleteLastExchange}` and `disabled={scene.finished}` to `<MessageList>`. **Why**: `ScenePage` holds `scene` state and owns `storyId`/`sceneId` from router params — it is the correct owner of the API calls and state update.

4. **File: index.css** — Add hover styles for the delete button inside message bubbles (hide by default, show on `.message-bubble:hover`), using `--accent` / `--border` / `--text` variables. This keeps the chat uncluttered and matches the standard pattern already described for the edit button. **Why**: without hiding on non-hover, every bubble shows a delete icon at all times, adding visual noise.

---

#### Test Coverage Gaps

- No frontend tests exist. Tests that should accompany the fix:
  - `MessageItem` renders a delete button when `onDelete` is provided and does not render one when it is absent.
  - Clicking the delete button calls `onDelete` with the correct `message.id`.
  - `MessageList` passes `onDelete` only to the last user message bubble, not to assistant messages or non-last user messages.
  - `ScenePage` handler calls `deleteMessage` for both the user message and the following assistant message, and removes both from state.

---

#### Risks / Edge Cases

- **Sequential deletes are not atomic**: the frontend calls `deleteMessage` twice (user message, then assistant). If the second call fails, the user message is already deleted but the orphaned assistant message remains. For MVP on a local single-user app this is acceptable, but the implementer should at minimum show an error if the second delete fails and reflect the partial state in the UI (the user message will already be gone from the YAML).
- **Last user message with no following assistant**: this can happen if manual YAML editing produced a trailing user message. The handler already guards this (`if (assistantMsg)`), but `MessageList` should still show the delete icon so the user can clean up.
- **Disable during in-flight requests**: if a `play` request is in flight, the delete button should be disabled (same shared `busy` state as the edit feature). Otherwise a user could delete while a play response is being written.
- **Scene finished**: the delete button must not appear (or must be disabled) when `scene.finished === true` — handled by passing `disabled={scene.finished}` to `MessageList` and not forwarding `onDelete` when `disabled`.
- **First assistant message (entry point)**: the entry point message (id=1, role=assistant) is never the "following assistant message" after a user message unless there are no user messages yet. In that edge case `lastUserIdx` is -1 and no delete button is rendered — correct behavior.

----------------------------------------------------------------------------------------------------

### Regenerate message ❌
- UI: No icon for regenerating for last assistant message and no functionality for it (I want to be able to regenerate last assistant message).

#### Problem Summary

The scene page has no regenerate affordance on the last assistant message. `MessageItem` renders static bubbles with no action buttons. `MessageList` passes no action props to `MessageItem`. `ScenePage` never imports `playScene` (the closest reusable API call). There is also **no backend endpoint** dedicated to regeneration — `POST /play` always appends a *new* user message plus a new assistant message to history, so it cannot be used directly to replace only the last assistant reply.

---

#### Expected Behavior

When a scene is active (not finished) and the last message is an assistant message, a regenerate icon should be visible on that bubble. Clicking it should:
1. Replace the last assistant message with a fresh LLM response generated from the **same** preceding user message (which stays in the history).
2. Update the message list in state without a full page reload.

---

#### Root Cause

The feature is missing at **two levels** — backend and frontend.

#### Backend gap

`POST /play` ([scenes.py lines 61–86](backend/app/api/routers/scenes.py#L61-L86), `ScenePlayService.play` scene_play_service.py) always:
- Appends the caller-supplied `user_content` as a new user message.
- Then appends a new assistant message.

There is **no endpoint** that can invoke the LLM against the current history and replace only the last assistant message. Using `DELETE` + `POST /play` from the frontend would duplicate the last user message (the user message is already in the YAML history; calling `/play` with it again would add a second copy).

#### Frontend gap

Even if the backend had the endpoint, the full frontend call chain is absent:

| File | Gap |
|---|---|
| MessageItem.jsx | No `onRegenerate` prop, no regenerate icon/button |
| MessageList.jsx | No `onRegenerate` prop, no logic to identify the last assistant message |
| ScenePage.jsx | No handler, no API call wiring, `playScene` not imported |

---

#### Evidence

`ScenePlayService.play` lines 35–51:
```python
# Always appends user_content as a new message — cannot skip this
user_msg = Message(id=user_id, role="user", content=user_content)
assistant_msg = Message(id=assistant_id, role="assistant", content=reply)
await self._scene_repo.add_message(story_id, scene_id, user_msg)
await self._scene_repo.add_message(story_id, scene_id, assistant_msg)
```

scenes.js has `playScene`, `deleteMessage` — no `regenerateLastAssistantMessage`. A frontend-only workaround would require 3 sequential, non-atomic calls.

All 116 backend tests pass; no test covers a regeneration path because no such path exists yet.

---

#### Fix Plan

##### Backend

**1. [backend/app/services/scene_play_service.py]** — Add a `regenerate` method:
- Load metadata, verify scene is not finished, raise `ValueError("scene_finished")` if so.
- Load current messages. Verify the last message exists and has `role == "assistant"`; if not, raise `ValueError("no_assistant_message")`.
- Find the preceding user message (second-to-last message, expected `role == "user"`). Build `SceneContext` using all messages **up to but not including** the last assistant message (i.e. pass the existing history minus that assistant message as the LLM context).
- Call `self._llm_client.invoke(context, last_user_message.content)` — same signature as `play`.
- Update the last assistant message in place via `self._scene_repo.update_message(story_id, scene_id, last_assistant_id, reply)`.
- Return the updated `Message`.
- **Why**: this is the only backend-safe approach — it replaces the assistant message without touching the user message, keeping IDs stable.

**2. [backend/app/api/routers/scenes.py]** — Add a new route `POST /{story_id}/scenes/{scene_id}/regenerate`:
- No request body.
- Delegate to `ScenePlayService.regenerate(story_id, scene_id)`.
- Return `{"data": {"assistant_message": {id, role, content}}}`.
- Map `KeyError` → 404, `ValueError("scene_finished")` → 409 `scene_finished`, `ValueError("no_assistant_message")` → 409 with a new `no_assistant_message` code, LLM exceptions → 502.
- **Why**: a dedicated endpoint keeps the contract clean; the frontend needs only one call, and it is safe to retry (idempotent in spirit — keeps same user message, replaces assistant reply).

**3. [backend/app/models/api.py]** — Add a `RegenerateResponse` Pydantic model with a single data field containing a `MessageOut` (same shape as the existing `UpdateMessageResponse.data`). **Why**: router needs a typed response model.

##### Frontend

**4. [frontend/src/api/scenes.js]** — Add a `regenerateLastAssistantMessage(storyId, sceneId)` function that calls `POST /api/stories/{storyId}/scenes/{sceneId}/regenerate` with no body. **Why**: centralises the HTTP call in the API layer, matching the existing pattern.

**5. [frontend/src/components/MessageItem.jsx]** — Add an `onRegenerate` prop. When provided (non-null), render a regenerate icon button on the bubble (e.g. ↺). Clicking it calls `onRegenerate()`. Show it only on assistant bubbles (already handled by the caller deciding which item gets the prop). **Why**: this is the only per-message action site in the render tree.

**6. [frontend/src/components/MessageList.jsx]** — Accept `onRegenerate` and `disabled` props. Compute the last assistant message index:
```js
const lastAssistantIdx = messages.map(m => m.role).lastIndexOf('assistant')
```
Pass `onRegenerate` only to the `MessageItem` at `lastAssistantIdx`, and only when `!disabled`. **Why**: regeneration is scoped to the last assistant bubble; giving every bubble the control would be confusing and incorrect.

**7. [frontend/src/pages/ScenePage.jsx]** — Import `regenerateLastAssistantMessage`. Add a handler:
```js
async function handleRegenerate() {
  const res = await regenerateLastAssistantMessage(storyId, sceneId)
  setScene(prev => ({
    ...prev,
    messages: prev.messages.map(m =>
      m.id === res.data.assistant_message.id ? res.data.assistant_message : m
    )
  }))
}
```
Pass `onRegenerate={handleRegenerate}` and `disabled={scene.finished}` to `<MessageList>`. **Why**: `ScenePage` owns `scene` state and the route params.

---

#### Test Coverage Gaps

- **[backend/tests/services/test_scene_play_service.py]** — Add tests for `ScenePlayService.regenerate`:
  - succeeds: replaces last assistant message, returns updated `Message`.
  - raises `ValueError("scene_finished")` when scene is finished.
  - raises `ValueError("no_assistant_message")` when no messages or last message is not assistant.
  - LLM failure does not corrupt stored messages.
- **[backend/tests/]** — No router-level integration test for `POST /regenerate` (404, 409, 502 paths).
- No frontend tests exist for `MessageItem`, `MessageList`, `ScenePage`.

---

#### Risks / Edge Cases

- **LLM failure atomicity**: `play` guards against corruption by not writing if the LLM throws. `regenerate` must do the same — call the LLM first, only call `update_message` after a successful reply.
- **No preceding user message**: if the last assistant message is the entry-point (message id=1, no prior user message), `regenerate` must still work — pass an empty message list as history and the `entry_point` text as the user content substitute, or raise `ValueError("no_user_message")` and block the icon at the UI level. Decide on policy before implementing; the simplest safe choice is to **not show the regenerate icon** if the last assistant message has no preceding user message (i.e. `lastAssistantIdx == 0` and messages[0].role == "assistant").
- **Busy/in-flight state**: if a `play` request is in flight, the regenerate button must be disabled (same shared `busy` state as edit/delete). `ScenePage` should lift this state.
- **Shared `disabled` semantics**: the `disabled` prop on `MessageList` already means "scene is finished". In-flight loading needs a separate `busy` flag, or the meaning of `disabled` must be broadened to `disabled || busy`.
- **New error code `no_assistant_message`**: not currently in endpoints.md's `Common error codes` list — the implementer should add it to both the doc and the error handling logic.

----------------------------------------------------------------------------------------------------

### System prompt correction ❌
- System prompt: review. Suspect that all messages are put in it instead of passing as a chain of messages. No scenes summaries in context.

#### Problem Summary

Two related gaps exist in the LLM invocation path. First, the existing scene message history (all prior turns stored in `messages.yaml`) is loaded and placed in `SceneContext.messages` but is **never forwarded to the LLM** — only a `SystemMessage` + a single `HumanMessage` for the current input are sent, so the model has zero conversational memory within a scene. Second, `SceneContext.context_data` — which renders as `# Context Data` in the system prompt and is the natural slot for narrative background — is always empty because `ScenePlayService.play()` never populates it with summaries from previously-finished scenes.

---

#### Expected Behavior

- Each LLM call should receive the full in-scene conversation chain: `SystemMessage` (scene config/characters) → alternating `AIMessage`/`HumanMessage` for all prior turns → `HumanMessage` for the current user input. This is standard LangChain multi-turn usage.
- `# Context Data` in the system prompt should contain the ordered summaries of all previously-finished scenes (taken from `story.yaml`'s `scenes[].summary` fields), so the model knows what happened before the current scene.

---

#### Root Cause

##### Issue 1 — Message history silently dropped

**File**: scene_llm_client.py

```python
async def invoke(self, context: SceneContext, user_message: str) -> str:
    system_prompt = self._prompt_builder.build_system_prompt(context)
    messages = [SystemMessage(system_prompt), HumanMessage(user_message)]  # ← history ignored
    response = await self._model.ainvoke(messages)
```

`context.messages` is accepted but never accessed. The LangChain call always receives exactly two messages regardless of how long the conversation is.

##### Issue 2 — `PromptBuilder` never reads `context.messages`

**File**: prompt_builder.py

`build_system_prompt` uses `context.scene_description`, `context.characters`, and `context.context_data` — but there is no reference to `context.messages` anywhere in the builder. So even if someone wanted to embed history in the system prompt, `PromptBuilder` wouldn't include it.

##### Issue 3 — `context_data` always empty; no scene summaries

**File**: scene_play_service.py

```python
context = SceneContext(
    scene_description=metadata.scene_description,
    characters=characters,
    messages=messages,
    # context_data= not supplied → defaults to []
)
```

`ScenePlayService` has no `StoryRepository` dependency and never fetches prior scenes' summaries. `context_data` always renders as `(no context)` in the system prompt. The data is available: `StoryRepository.get_story()` returns `StoryMeta.scenes[].summary` (a `list[str] | None` per scene), populated from `story.yaml`.

---

#### Evidence

- scene_llm_client.py: `messages = [SystemMessage(system_prompt), HumanMessage(user_message)]` — hardcoded 2-element list, `context.messages` never accessed.
- prompt_builder.py — no method references `context.messages`.
- scene_play_service.py: `SceneContext(...)` constructed with `context_data` absent.
- test_scene_llm_client.py: `_make_context()` always uses `messages=[]` — the test never exercises the history path and would not catch a regression.
- test_prompt_builder.py: no test asserts that `context.messages` appears anywhere in the output (because it currently doesn't).
- 116/116 backend tests pass — the bug is not caught by any existing test.

---

#### Fix Plan

**1. [backend/app/llm/scene_llm_client.py]** — Convert `context.messages` to LangChain message objects and insert them between the system message and the current user message:
```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

async def invoke(self, context: SceneContext, user_message: str) -> str:
    system_prompt = self._prompt_builder.build_system_prompt(context)
    history = [
        AIMessage(m.content) if m.role == "assistant" else HumanMessage(m.content)
        for m in context.messages
    ]
    messages = [SystemMessage(system_prompt)] + history + [HumanMessage(user_message)]
    response = await self._model.ainvoke(messages)
    return response.content
```
**Why**: this is the correct LangChain multi-turn pattern; `context.messages` is already available, it just isn't used.

**2. [backend/app/services/scene_play_service.py]** — Add `StoryRepository` as a constructor dependency and populate `context_data` with the ordered summaries of all finished scenes that precede the current one:
```python
# in __init__: add story_repo: StoryRepository
# in play():
story_meta = await self._story_repo.get_story(story_id)
context_data = [
    line
    for s in story_meta.scenes
    if s.finished and s.id < scene_id and s.summary
    for line in s.summary
]
context = SceneContext(
    scene_description=metadata.scene_description,
    characters=characters,
    messages=messages,
    context_data=context_data,
)
```
**Why**: `story.yaml` already stores `scenes[].summary` (written by `SceneLifecycleService.finish_scene`); `StoryRepository.get_story()` already returns it; this is the correct place to assemble narrative background before calling the LLM.

**3. [backend/app/api/dependencies.py]** — Update `get_scene_play_service()` to inject `StoryRepository` into `ScenePlayService`.  
**Why**: the dependency injection wiring must match the new constructor signature.

---

#### Test Coverage Gaps

- **[backend/tests/llm/test_scene_llm_client.py]** — Add a test that builds a context with non-empty `messages` and asserts the LangChain model receives `len(messages) + 2` message objects (system + history + current user), with correct roles and ordering.
- **[backend/tests/services/test_scene_play_service.py]** — Add a test that verifies `SceneContext` is constructed with `context_data` populated from the story's finished-scene summaries when a `StoryRepository` mock returns a story with finished scenes.
- **[backend/tests/services/test_scene_play_service.py]** — Add a test that verifies `context_data` is empty when there are no finished scenes before the current scene.

---

#### Risks / Edge Cases

- **Entry-point duplication**: the `entry_point` text is stored in `scene_description.entry_point` (rendered in `# Scene Configuration` of the system prompt) **and** as the first assistant message in `messages.yaml` (id=1, role=assistant). After fix 1, this text will appear twice in the LangChain call: once in the system prompt and once as the first `AIMessage` in history. This is mildly redundant but likely harmless for the LLM. The clean fix is to skip the first assistant message (id=1) when converting history, but that requires knowing which message is the entry-point — simplest rule: skip `messages[0]` if `messages[0].role == "assistant"`. Decide on policy before implementing.
- **Token budget**: passing the full conversation history increases token usage per call as the scene grows. For MVP on a local model this is acceptable, but the implementer should be aware of potential context-length limits on long scenes.
- **`story_repo.get_story()` failure**: if `story.yaml` is missing when `ScenePlayService.play()` is called, a `KeyError` will propagate. The router already maps `KeyError` → 404, so behavior is consistent, but it is a new failure mode for `/play` that did not exist before.
- **Scene ordering for summaries**: the filter `s.id < scene_id` assumes scene IDs are ordered chronologically. Per data_storage_structure.md, scenes are ordered by position in the `scenes` list — IDs may not be strictly sequential. A safer filter is to collect summaries of all scenes that appear *before* the current scene's index in `story_meta.scenes`, not by ID comparison. 

===


## Not planned:

### Problems
- Readme for LLM about how to run tests
- Review async calls for ones that are sequential but could be parallel.
- SceneLLMClient.invoke() method also responsible for building the system prompt and messages. This is a smell that the responsibilities are not well-separated. The client should be focused on calling the LLM with a given context.

### Enhancements
- No user character card in a story data. No place for it in the system prompt. (As a user I want to play different roles in a story. Since all personality related traits will be a user responsobility, the card should contain a user character appearance so LLM can use it in the system prompt to create more personalized and immersive responses)
