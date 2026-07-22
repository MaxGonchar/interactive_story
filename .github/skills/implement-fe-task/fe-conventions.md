# Frontend UI Test Convention

This document is the authoritative reference for all frontend tests in this project. It is used by the `implement-fe-task` and `review-fe` skills.

---

## Tooling

| Role | Library |
|---|---|
| Runner | Vitest |
| Component rendering | `@testing-library/react` |
| User interactions | `@testing-library/user-event` (prefer over `fireEvent`) |
| Extended matchers | `@testing-library/jest-dom` |
| Environment | jsdom |

---

## File Location

Tests are **colocated** with the source file they test:

```
frontend/src/components/MessageItem.jsx
frontend/src/components/MessageItem.test.jsx

frontend/src/api/scenes.js
frontend/src/api/scenes.test.js
```

---

## Naming

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

---

## What to Test

- What the user **sees**: text content, labels, button presence/absence
- What the user **does**: clicks, types, submits
- **State transitions**: loading → loaded, default → editing, enabled → disabled
- **Error paths**: API throws → error message appears

## What NOT to Test

- CSS class names (implementation detail)
- Internal component state directly
- Exact inline styles
- Third-party library internals (e.g. ReactMarkdown rendering)

---

## Mocking API Modules

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

---

## Test Data

Use factory functions from `frontend/src/tests/factories.js`, never inline raw objects.

```js
import { makeMessage, makeScene } from '../tests/factories'

const msg = makeMessage({ role: 'user', content: 'Hello' })
```

---

## Async Interactions

Use `await userEvent.click(...)` and `await screen.findByText(...)` for async state changes. Never use arbitrary `setTimeout` or `waitFor` with time delays.

---

## API Module Tests (Layer 1)

Mock the global `fetch`. Assert URL, method, headers, and body. Assert error throw on non-ok response.

```js
global.fetch = vi.fn()

it('throws on non-ok response', async () => {
  fetch.mockResolvedValue({ ok: false, json: async () => ({ error: { message: 'Not found' } }) })
  await expect(getScene('s1', 'sc1')).rejects.toThrow('Not found')
})
```

---

## Running Tests

```bash
make test-fe
```

Always run via `make test-fe` from the project root.
