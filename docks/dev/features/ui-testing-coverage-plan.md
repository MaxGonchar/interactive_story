# UI Test Coverage Plan

**Status**: Draft  
**Date**: 2026-07-22  
**Reference**: [ui-testing-harness.md](./ui-testing-harness.md)

This document is the input backlog for `create-tasks`. Each section is a logical task group. Priority: P1 → P2 → P3.

---

## P0 — Infrastructure (prerequisite for everything else)

### Task: Set up Vitest + RTL test infrastructure

**Files to change:**
- `frontend/package.json` — add dev deps, add `test` / `test:watch` scripts
- `frontend/vite.config.js` — add `test` block with jsdom environment and setup file
- `frontend/src/tests/setup.js` — import `@testing-library/jest-dom`
- `frontend/src/tests/factories.js` — factory functions: `makeMessage()`, `makeScene()`, `makeStory()`
- `Makefile` — add `test-fe` target

**Done when:** `make test-fe` runs and exits 0 on an empty test suite.

---

## P1 — High-value shared components

### Task: Tests for `MessageItem`

The most complex shared component. Multiple behavior branches.

**Test cases:**
- renders "You" label for user messages
- renders "Narrator" label for assistant messages
- shows edit button when `onEdit` is provided and `disabled` is false
- does not show edit button when `disabled` is true
- clicking edit button switches to edit mode (textarea appears)
- Save button is disabled when draft equals original content
- Save button is disabled when draft is empty
- Save button is enabled when draft differs from original
- clicking Save calls `onEdit` with correct message id and new content
- clicking Cancel restores original content and exits edit mode
- shows Regenerate button for assistant messages when `onRegenerate` is provided
- does not show Regenerate button for user messages
- Save button shows disabled state while save is in-flight

---

### Task: Tests for `MessageComposer`

**Test cases:**
- renders a textarea and a Send button
- Send button is disabled when textarea is empty
- Send button is disabled when `disabled` prop is true
- Send button is enabled when textarea has non-whitespace content
- clicking Send calls `onSend` with trimmed text
- textarea is cleared after successful send
- textarea retains content when `onSend` throws (retry scenario)
- placeholder text changes based on `disabled` prop

---

### Task: Tests for `FinishModal`

Contains internal async state (generate summary) and validation logic.

**Test cases:**
- renders modal overlay with "Finish Scene" heading
- Submit button is present
- clicking Submit with empty items shows validation error
- clicking Submit with valid items calls `onSubmit` with the items
- clicking Cancel calls `onCancel`
- clicking "Generate" calls `generateSceneSummary` and populates items on success
- Generate button is disabled while generation is in-flight
- shows error message when `generateSceneSummary` throws

---

### Task: Tests for `api/scenes.js`

Pure fetch wrappers — straightforward to cover completely.

**Test cases:**
- `getScene`: calls correct URL with GET
- `playScene`: calls correct URL with POST, correct JSON body
- `editMessage`: calls correct URL with PUT, correct JSON body
- `deleteMessage`: calls correct URL with DELETE
- `finishScene`: calls correct URL with POST, correct JSON body
- `regenerateLastAssistantMessage`: calls correct URL with POST
- `generateSceneSummary`: calls correct URL with GET
- all functions throw with the API error message on non-ok response

---

## P2 — Secondary shared components and API modules

### Task: Tests for `SceneActions`

**Test cases:**
- when `finished` is true, renders the scene summary text
- when `finished` is true, renders "No summary available." if `sceneSummary` is null
- when `finished` is false, renders a textarea and Finish Scene button
- Finish Scene button is disabled when textarea is empty
- clicking Finish Scene calls `onFinish` with trimmed summary text

---

### Task: Tests for `MessageList`

**Test cases:**
- renders a message for each item in the list
- passes correct `onEdit`, `onDelete`, `onRegenerate` props to each `MessageItem`
- renders empty state without crashing when list is empty

---

### Task: Tests for `StoryList`

**Test cases:**
- renders a list item for each story
- each item shows the story title
- clicking a story item navigates to the correct story URL

---

### Task: Tests for `SceneList`

**Test cases:**
- renders a list item for each scene
- each item shows the scene title/name
- clicking a scene item navigates to the correct scene URL

---

### Task: Tests for `BulletTextarea`

Used inside `FinishModal`. Custom multi-line bullet input.

**Test cases (to be specified after reading the component source):**
- renders current items as text
- onChange is called when user edits content
- respects `disabled` prop

---

### Task: Tests for `api/stories.js`

**Test cases:**
- `getStories`: calls correct URL with GET
- `getStory`: calls correct URL with GET
- throws with API error message on non-ok response

---

### Task: Tests for `api/characters.js` and `api/choice_driven.js`

**Test cases:** mirror `api/stories.js` pattern — one test per exported function for happy path + error throw.

---

## P3 — Page smoke tests (deferred)

Low priority. Mount each page with mocked API, assert it renders without crashing through its loading → data states.

### Task: Smoke tests for `StoriesPage`
- renders loading state
- renders stories list on success
- renders error message on API failure

### Task: Smoke tests for `StoryPage`
- renders loading state
- renders scene list on success
- renders error message on API failure

### Task: Smoke tests for `ScenePage`
- renders loading state
- renders message list on success
- renders error message on API failure

---

## Notes for task creation

- P0 must be completed before any other task can be verified
- P1 tasks are independent of each other and can be parallelized
- P2 tasks depend on P0 infrastructure only
- P3 tasks should be created only after P1+P2 are done and the team has a feel for the test style
