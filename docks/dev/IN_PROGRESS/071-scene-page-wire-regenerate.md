# Task 071: Wire Regenerate Handler in ScenePage

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Import `regenerateLastAssistantMessage` into `ScenePage` and add a `handleRegenerate` async handler. The handler calls the API, then updates `scene.messages` in state by replacing the message whose `id` matches the returned `assistant_message.id`. Pass `onRegenerate={handleRegenerate}` and `disabled={scene.finished}` to `<MessageList>`. The regenerate button must be disabled while any async operation is in flight (use the existing or a new `busy` state flag).

## Scope

What IS included:
- Import `regenerateLastAssistantMessage` from `../api/scenes`
- `handleRegenerate` async function that:
  1. Sets `busy = true`
  2. Calls `regenerateLastAssistantMessage(storyId, sceneId)`
  3. Updates `scene.messages` in state, replacing the matching message by `id`
  4. Sets `busy = false` in a `finally` block
- `onRegenerate={handleRegenerate}` passed to `<MessageList>`
- `disabled={scene.finished || busy}` passed to `<MessageList>` (if a `busy` state already exists, extend it; otherwise add one)
- Error display: show an error message in state if the API call throws (consistent with existing error handling pattern in `ScenePage`)

What is NOT included (deferred):
- Changes to `MessageItem` or `MessageList` (tasks 069, 070)
- CSS styling (task 072)

## Deliverable

Updated `frontend/src/pages/ScenePage.jsx`:

```
frontend/src/pages/ScenePage.jsx
```

## Acceptance Criteria

- [ ] Clicking the regenerate button on the last assistant message triggers an API call to `POST /regenerate`
- [ ] The last assistant message in the rendered list is replaced with the new content after a successful response
- [ ] No full page reload occurs
- [ ] The regenerate button is disabled while the request is in flight
- [ ] The regenerate button is disabled when `scene.finished === true`
- [ ] An error is displayed if the API call fails
- [ ] Frontend builds without errors

## Test Notes

Manual end-to-end:
1. Open an active scene with at least two messages (one user, one assistant).
2. Click the regenerate (↺) button on the last assistant bubble.
3. Observe spinner/disabled state while the LLM responds.
4. Verify the assistant message content changes to the new reply.
5. Verify the user message immediately before it is unchanged.

## Dependencies

- 068 (API function)
- 069 (MessageItem regenerate button)
- 070 (MessageList forwarding)
- 066 (backend endpoint)
