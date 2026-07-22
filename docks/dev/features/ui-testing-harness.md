# Feature: UI Testing Harness

**Status**: Draft  
**Date**: 2026-07-22

## Summary

Introduce a frontend testing infrastructure using Vitest and React Testing Library, establish a project-wide UI test convention, and extend the AI harness (skills) to cover React development. The primary goal is a regression net for shared components — catching the class of bug where a change to one component silently breaks another page.

## Value

- **Problem it solves**: shared component changes cause silent regressions on unrelated pages. Currently there is zero automated safety net on the frontend.
- **How it fits**: the backend already has pytest + a testing convention enforced by the `implement-task` and `review-be` skills. The frontend needs the same discipline to keep pace with growing UI complexity.
- **Success criteria**: a broken shared component (e.g. `MessageItem`) causes at least one test to fail before the change reaches manual testing.

## Scope

### In scope for first iteration
- Tooling setup: Vitest + React Testing Library + jsdom
- Project-wide UI test convention document (referenced by AI skills)
- `review-fe` skill — periodic quality checker for React code, mirrors `review-be`
- Split `implement-task` into `implement-be-task` and `implement-fe-task`; `implement-fe-task` includes writing tests as part of the definition of done
- Test infrastructure files: `vite.config.js` test block, `frontend/src/tests/setup.js`, `frontend/src/tests/factories.js`
- `make test-fe` command in the Makefile

### Out of scope / future
- End-to-end tests (Playwright / Cypress)
- Visual regression tests
- Coverage thresholds / CI enforcement
- Page-level integration tests (deferred; tracked in coverage plan as P3)

## User Flow

This is a developer-facing feature. The flow is:

1. Developer runs `make test-fe` — Vitest runs all `*.test.jsx` / `*.test.js` files and reports pass/fail.
2. When implementing a FE task via `implement-fe-task`, Copilot automatically writes RTL tests for the new/changed component before marking the task done.
3. Periodically, developer invokes `review-fe` — Copilot scans the frontend for quality issues and missing test coverage, produces a report.

## API Changes

None.

## Data Changes

None.

## Backend Changes

None.

## Frontend Changes

### Infrastructure files

| File | Change |
|---|---|
| `frontend/package.json` | Add dev dependencies: `vitest`, `@testing-library/react`, `@testing-library/user-event`, `@testing-library/jest-dom`, `jsdom`; add `"test": "vitest run"` and `"test:watch": "vitest"` scripts |
| `frontend/vite.config.js` | Add `test: { environment: 'jsdom', setupFiles: ['./src/tests/setup.js'], globals: true }` block |
| `frontend/src/tests/setup.js` | Import `@testing-library/jest-dom` for extended matchers |
| `frontend/src/tests/factories.js` | Factory functions for test data: `makeMessage()`, `makeScene()`, `makeStory()` |

### AI harness files

| File | Change |
|---|---|
| `.github/skills/implement-fe-task/SKILL.md` | New skill, split from `implement-task`, React/RTL-aware, tests are part of done |
| `.github/skills/implement-fe-task/fe-conventions.md` | Convention reference doc (see section below) |
| `.github/skills/review-fe/SKILL.md` | New skill, quality checker for React components |
| `.github/skills/implement-be-task/SKILL.md` | Renamed/split from `implement-task`, Python/pytest-aware |

## UI Test Convention

This section defines the authoritative convention referenced by `implement-fe-task` and `review-fe`.

### Tooling
- **Runner**: Vitest
- **Component rendering**: `@testing-library/react`
- **User interactions**: `@testing-library/user-event` (prefer over `fireEvent`)
- **Extended matchers**: `@testing-library/jest-dom`
- **Environment**: jsdom

### File location
Tests are colocated with the source file they test:
```
frontend/src/components/MessageItem.jsx
frontend/src/components/MessageItem.test.jsx
frontend/src/api/scenes.js
frontend/src/api/scenes.test.js
```

### Naming
```js
describe('MessageItem', () => {
  it('renders user message with "You" label', () => { ... })
  it('renders assistant message with "Narrator" label', () => { ... })
  it('enters edit mode when edit button is clicked', () => { ... })
})
```
- `describe` block = component or module name
- `it` statement = one observable behavior from the user's perspective
- No "should" prefix — keep it plain and readable

### What to test
- What the user **sees**: text content, labels, button presence/absence
- What the user **does**: clicks, types, submits
- **State transitions**: loading → loaded, default → editing, enabled → disabled
- **Error paths**: API throws → error message appears

### What NOT to test
- CSS class names (implementation detail)
- Internal component state directly
- Exact inline styles
- Third-party library internals (e.g. ReactMarkdown rendering)

### Mocking API modules
Use `vi.mock` at the module level. Always reset mocks between tests.
```js
import { editMessage } from '../api/scenes'
vi.mock('../api/scenes')

beforeEach(() => {
  vi.resetAllMocks()
})

it('calls editMessage with correct args on save', async () => {
  editMessage.mockResolvedValue({ data: { ... } })
  // render, interact, assert
})
```

### Test data
Use factory functions from `frontend/src/tests/factories.js`, never inline raw objects.
```js
import { makeMessage, makeScene } from '../tests/factories'

const msg = makeMessage({ role: 'user', content: 'Hello' })
```

### Async interactions
Use `await userEvent.click(...)` and `await screen.findByText(...)` for async state changes. Never use arbitrary `setTimeout` or `waitFor` with time delays.

### API module tests (Layer 1)
Mock the global `fetch`. Assert URL, method, headers, and body. Assert error throw on non-ok response.
```js
global.fetch = vi.fn()

it('throws on non-ok response', async () => {
  fetch.mockResolvedValue({ ok: false, json: async () => ({ error: { message: 'Not found' } }) })
  await expect(getScene('s1', 'sc1')).rejects.toThrow('Not found')
})
```

## Open Questions

- Should `make test-fe` run in watch mode locally and CI mode in `pre-push`? Or always CI mode?
- Should `implement-be-task` reuse the body of the current `implement-task` skill verbatim, or be a fresh rewrite?

## Risks

- `import.meta.env` references (e.g. `VITE_API_BASE_URL` in API modules) require Vitest's `define` or env setup — needs a one-time config fix.
- `react-markdown` + `remark-gfm` render in jsdom without issues but produce verbose DOM; tests for `MessageItem` should avoid asserting on markdown output internals.
- Colocating test files means they appear alongside source in the file tree — acceptable tradeoff for discoverability.
