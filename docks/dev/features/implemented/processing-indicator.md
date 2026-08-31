# Feature: Processing Indicator

**Status**: Draft  
**Date**: 2026-08-30

## Summary
When the user triggers an LLM-backed operation (sending a message, regenerating a message, generating a scene summary, generating/regenerating choices, selecting a choice), the UI currently only disables controls with no other feedback. This feature introduces a shared, reusable "verb + pulsing dots" indicator so the user always knows the system is actively working, applied consistently across every LLM-call action in the app.

## Value
- **Problem solved**: Users have no feedback that a slow (LLM) request is in flight, leading to uncertainty and possible repeated clicks.
- **Fit**: Directly supports the core scene-playing flow, the app's primary value; also benefits the choice-driven play flow.
- **Success criteria**: every LLM-triggering control in the app visibly communicates "working" state via a consistent pattern; user never sees a silently-disabled control during an LLM call.

## Scope
### In scope
- A reusable `ProcessingLabel` (verb + pulsing dots) component.
- Applied to all LLM-call operations:
  - `ScenePage` → Send message
  - `MessageItem` → Regenerate message (icon-triggered)
  - `FinishModal` → Generate scene summary
  - `ChoiceDrivenStoryPage` / `ChoicesGrid` → Generate choices, Regenerate choices
  - `ChoicesGrid` → Select choice
- Two placements of the same component:
  - **Button variant**: button label text replaced by `{Verb}…` + animated dots; button width stays fixed (no layout jump).
  - **Message-frame variant**: the entire message bubble body (markdown content + action icon row) is replaced by `{Verb}…` + animated dots.
- While any one operation is processing, all other interactive controls in the affected view remain disabled (existing `busy` pattern) but do **not** themselves show the animation — only the triggered control does.

### Out of scope / future
- Non-LLM operations (edit message, delete message, edit step text, return to step, finish-scene submit) — these stay on the existing disable-only pattern for now.
- Cancel/abort of an in-flight LLM request.
- Progress percentage or estimated time remaining.

## User Flow
1. User clicks a control that triggers an LLM call (e.g. "Send", the regenerate icon, "Generate Summary", "Generate choices", a choice button).
2. The triggered control immediately swaps its content for `{Verb}…` with pulsing dots.
3. All other interactive controls in the current view become disabled (no animation) for the duration of the call.
4. On success, the control returns to its normal state and the result (new message, new summary, new choices, new step) appears.
5. On failure, the control returns to normal state and the existing inline error message (`opError` / `generateError`) is shown, as today.

## API Changes
None — this is a frontend-only change; no backend/API contract changes.

## Data Changes
None.

## Backend Changes
None.

## Frontend Changes
- **New component** `frontend/src/components/ProcessingLabel.jsx`: renders `{verb}` text followed by an animated three-dot indicator (CSS animation via a class, e.g. `.processing-dots`, defined in `frontend/src/index.css` per the style guide — no magic values, only CSS variable tokens for color/spacing).
- **`frontend/src/components/MessageComposer.jsx`**: Send button renders `<ProcessingLabel verb="Sending" />` instead of "Send" while `disabled`/sending; fixed `min-width` added to avoid layout shift.
- **`frontend/src/components/MessageItem.jsx`**: when a regenerate is in flight for this message, replace the bubble body (markdown + `.message-actions` row) with `<ProcessingLabel verb="Regenerating" />`. Requires the parent (`ScenePage`) to pass down which message id is currently regenerating (e.g. a `regeneratingMessageId` prop) since today's `busy` flag is scene-wide.
- **`frontend/src/components/FinishModal.jsx`**: "Generate Summary" button renders `<ProcessingLabel verb="Generating" />` while `isGenerating`; fixed button width.
- **`frontend/src/components/ChoicesGrid.jsx`**: "Regenerate" button and each choice button render `<ProcessingLabel verb="…" />` for the one actually clicked (needs a way to know *which* control was clicked, e.g. a local `pendingAction` state: `'regenerate'` or the clicked choice key); others stay disabled without animation.
- **`frontend/src/pages/ChoiceDrivenStoryPage.jsx`**: "Generate choices" button renders `<ProcessingLabel verb="Generating" />` while `busy`; passes down which action is pending to `ChoicesGrid`.
- **`frontend/src/pages/ScenePage.jsx`**: tracks which specific message id (if any) is being regenerated, in addition to the existing scene-wide `busy` flag, and passes it to `MessageList`/`MessageItem`.
- All fixed button widths and animation timing/colors go through CSS variable tokens per `docks/dev/frontend_styles_guide.md`; no raw px/hex values.

## Open Questions
- Exact verb wording for "Select choice" (proposed: "Continuing") — confirm during implementation/review.
- Whether `ProcessingLabel`'s dot animation timing should be a fixed constant or configurable — default to a fixed constant unless a need for variation arises.

## Risks
- Tracking "which specific control is processing" (vs. a single scene-wide `busy` boolean) is a small state-shape change in `ScenePage` and `ChoicesGrid` — needs care to keep other controls correctly disabled without over-complicating state.
- Message-frame variant fully replaces bubble content, so bubble height may change during regeneration if the placeholder text is shorter/longer than original content — acceptable per "simplest implementation" decision, but worth a visual check during review.
