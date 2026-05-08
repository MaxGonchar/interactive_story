# Task 022: MessageComposer Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `MessageComposer` presentational component. Provides a textarea for user input and a Send button. Calls `onSend(content)` when the user submits. Disabled when the scene is finished.

## Scope

What IS included:
- `MessageComposer` component accepting `onSend(content)` and `disabled` props
- Textarea for message input
- Send button that calls `onSend` with the current input value and clears the textarea
- When `disabled` is `true`: textarea and button are disabled, placeholder text indicates scene is finished

What is NOT included (deferred):
- Actual API call (M6 — `ScenePage` will call `playScene` and pass result up)
- Character counter or max-length enforcement in UI (validation is backend-enforced)

## Deliverable

`frontend/src/components/MessageComposer.jsx` — a functional React component.

```
frontend/src/components/MessageComposer.jsx
```

## Acceptance Criteria

- [ ] Renders a textarea and a Send button
- [ ] Clicking Send calls `onSend` with the current textarea value (trimmed)
- [ ] Textarea is cleared after Send is called
- [ ] Send button is disabled when textarea is empty or `disabled` prop is `true`
- [ ] Textarea and button are disabled when `disabled` prop is `true`
- [ ] Component is the default export

## Test Notes

Render with `onSend={console.log}` and `disabled={false}`; type text, click Send, verify console log and textarea clears. Then render with `disabled={true}`; verify controls are disabled.

## Dependencies

None
