# Task 050: Remove Entry Point Paragraph from SceneHeader

**Feature:** Extra scene description fix
**Status:** TODO

## Description

`SceneHeader` renders `scene.scene_description.entry_point` as a static `<p>` tag, while the same text is already stored as message id=1 (`role: assistant`) in `messages.yaml` and displayed as the first chat bubble by `MessageList`. This causes the entry point text to appear twice on the scene page. This task removes the duplicate paragraph so the entry point appears only as the first assistant message.

## Scope

What IS included:
- Remove the `<p>{scene.scene_description.entry_point}</p>` line from `SceneHeader.jsx`

What is NOT included (deferred):
- Removing the `scene` prop from `SceneHeader` entirely (optional cleanup, out of scope)
- Any backend changes
- Adding frontend component tests

## Deliverable

Modified `SceneHeader.jsx` where the header renders only the scene ID and status badge — no description paragraph.

```
frontend/src/components/SceneHeader.jsx
```

## Acceptance Criteria

- [ ] `SceneHeader` no longer renders any text from `scene.scene_description.entry_point`
- [ ] The scene page shows the entry point text exactly once, as the first assistant message bubble rendered by `MessageList`
- [ ] All existing scene page functionality (scene ID display, status badge, finished state) is unaffected
- [ ] No console errors or prop-type warnings after the change

## Test Notes

Manual verification:
1. Start the app and navigate to an active scene that has the entry point stored as message id=1.
2. Confirm the entry point text appears only once — as the first chat bubble from the assistant.
3. Confirm `SceneHeader` shows only the scene identifier and status badge (e.g. "Active" / "Finished").
4. Navigate to a finished scene and confirm the same behaviour.

## Dependencies

none
