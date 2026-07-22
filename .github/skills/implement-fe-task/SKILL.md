---
name: implement-fe-task
description: "Implement frontend React changes from a task description passed as prompt text. Use when: implementing a frontend task, executing a React/Vite TODO item, starting work on a UI feature, fixing a frontend bug. Writing RTL tests is part of the definition of done. Produces a feature branch, a reviewed implementation plan, code changes, tests run with Vitest, and an open PR."
argument-hint: "Plain-text description of the frontend task to implement (e.g. 'Add an edit button to MessageItem that opens an inline input')"
---

# Implement Frontend Task

End-to-end workflow for implementing a single frontend task: branch → understand → plan → review → code → test → PR.

Tests are **part of the definition of done** — every new or changed component requires RTL tests before the task is considered complete.

## When to Use
- Implementing a specific React/Vite feature, fix, or refactor described in the prompt
- UI component work, API module work, or page-level changes

## Procedure

### 0. Verify GitHub CLI (`gh`)

Before any GitHub operation, confirm `gh` is available and authenticated.

```bash
if ! command -v gh &>/dev/null; then
  echo "gh not found"
else
  gh auth status
fi
```

**If `gh` is not installed**, guide the user through installation:

```bash
# macOS (Homebrew)
brew install gh

# Linux (apt)
sudo apt install gh

# Linux (dnf)
sudo dnf install gh

# Windows (winget)
winget install --id GitHub.cli
```

Official docs: https://cli.github.com/

**If `gh` is installed but not authenticated**, run:

```bash
gh auth login
```

Follow the prompts:
1. Select **GitHub.com**
2. Choose **HTTPS**
3. Authenticate via browser or paste a personal access token

Verify success with `gh auth status` before continuing.

> Do not proceed to step 1 until `gh auth status` reports a valid logged-in account.

---

### 1. Read the Task

The task description is provided directly as prompt text. Extract:
- **Goal**: what problem this solves or feature it delivers
- **Scope**: which files/components/pages are touched
- **Deliverable**: the concrete artifact to produce
- **Acceptance criteria**: the conditions for "done"
- **Test notes**: what behaviors to verify with RTL tests

### 2. Create and Switch to Branch

Determine the branch name from the task description — derive 2–4 words in kebab-case (e.g. `message-edit-button`):

```bash
git checkout main
git pull
git checkout -b <branch-name>
```

### 3. Read Architecture and Conventions

Read the following docs **before** planning. Do not skip.

| Doc | Purpose |
|-----|---------|
| [requirements.md](../../../../docks/dev/requirements.md) | Functional requirements and feature goals |
| [frontend_styles_guide.md](../../../../docks/dev/frontend_styles_guide.md) | Styling rules — no magic values, CSS classes for static styles, inline only for dynamic |
| [fe-conventions.md](./fe-conventions.md) | Test tooling, file location, naming, what/what-not to test, mocking, factories |

Also scan the relevant source files under `frontend/src/` to identify:
- Existing components, API modules, and utilities that can be reused
- Patterns already in use (prop shapes, API call conventions, loading/error state handling)
- Style (CSS variable usage, class naming, `styles.js` entries)

### 4. Draft an Implementation Plan

Write a numbered plan. Each step must state:
1. **What** — the specific change (file, component, function, CSS class)
2. **Why** — the motivation tied to the task goal or a convention from the docs
3. **How** — brief description of the approach

The plan must include a **"Write Tests"** step for every new or changed component or API module, listing the specific behaviors to be covered per [fe-conventions.md](./fe-conventions.md).

Rules during planning:
- **Reuse** existing components and helpers — do not reinvent
- **Mirror** the patterns already present in the codebase
- **Follow** the styling rules from `frontend_styles_guide.md` — no magic values, no inline styles for static properties
- Flag any ambiguity or missing information as explicit questions

Present the plan and **wait for user approval before writing any code**.

### 5. Incorporate Review Feedback

If the user requests changes to the plan:
- Update each affected step in place
- Re-present only the changed steps with a brief diff summary
- Do not proceed until the user confirms the revised plan

### 6. Implement Changes

Work step-by-step through the approved plan:
- Make one logical change at a time
- Do not add features, refactors, or comments beyond what the plan specifies
- Follow style rules strictly: every color, spacing size, font, and radius must use a CSS variable token

### 7. Write Tests

For every new or changed component or API module, write RTL tests following [fe-conventions.md](./fe-conventions.md):

- Tests are **colocated** with the source file (e.g. `MessageItem.test.jsx` next to `MessageItem.jsx`)
- Use factory functions from `frontend/src/tests/factories.js` for test data
- Mock API modules with `vi.mock`; reset with `vi.resetAllMocks()` in `beforeEach`
- Cover: what the user sees, what the user does, state transitions, error paths

The task is **not done** until the tests are written.

### 8. Run Tests

```bash
make test-fe
```

Always run via `make test-fe` from the project root.

Report results. Fix failures before proceeding.

### 9. Request User Review

Before committing, present a summary of all changes made:
- List every file that was created or modified (source + test files)
- Show a `git diff --stat` summary
- Ask the user to review and confirm they are happy with the changes

```bash
git diff --stat
```

Use `vscode_askQuestions` to ask:
> "Please review the diff above. Are you ready to commit and open a PR?"

Do **not** proceed to step 10 until the user explicitly confirms.

If the user requests changes:
- Implement the requested corrections
- Re-run tests if affected
- Re-present the summary and ask for confirmation again

### 10. Commit Changes

```bash
git add -A
git commit -m "<branch-name>: <short imperative summary>"
```

Commit message format: `message-edit-button: add inline edit mode to MessageItem`

### 11. Push Branch

```bash
git push -u origin <branch-name>
```

### 12. Open Pull Request

Use the GitHub CLI:
```bash
gh pr create \
  --title "<short summary>" \
  --body "<one-sentence description of changes>

Changes:
- <file or component changed and why>

How to test: <steps>" \
  --base main
```

Include in the PR body:
- Summary of changes made
- How to test / verify (manual steps + `make test-fe`)

## Completion Checklist

- [ ] `gh` installed and authenticated (`gh auth status` passes)
- [ ] Branch created from up-to-date `main`
- [ ] Task fully read and understood
- [ ] Architecture and convention docs read
- [ ] Plan reviewed and approved by user (includes test step)
- [ ] All plan steps implemented
- [ ] RTL tests written for every new/changed component or API module
- [ ] `make test-fe` passed
- [ ] User reviewed changes and approved commit
- [ ] Commit message follows convention
- [ ] Branch pushed
- [ ] PR open with description
