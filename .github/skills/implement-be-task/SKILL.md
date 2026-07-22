---
name: implement-be-task
description: "Implement backend changes from a task description passed as prompt text. Use when: implementing a backend task, executing a Python/FastAPI TODO item, starting work on a backend feature, fixing a backend bug. Produces a feature branch, a reviewed implementation plan, code changes, tests run with pytest, and an open PR."
argument-hint: "Plain-text description of the backend task to implement (e.g. 'Add a GET /scenes endpoint that returns all scenes for a story')"
---

# Implement Backend Task

End-to-end workflow for implementing a single backend task: branch → understand → plan → review → code → test → PR.

## When to Use
- Implementing a specific backend feature, fix, or refactor described in the prompt
- Python / FastAPI / pytest work

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
- **Scope**: which files/modules are touched
- **Deliverable**: the concrete artifact to produce
- **Acceptance criteria**: the conditions for "done"
- **Test notes**: what to verify

### 2. Create and Switch to Branch

Determine the branch name from the task description — derive 2–4 words in kebab-case (e.g. `add-scene-router`):

```bash
git checkout main
git pull
git checkout -b <branch-name>
```

### 3. Read Architecture and Conventions

Read the following docs **before** planning. Do not skip.

| Doc | Purpose |
|-----|---------|
| [plan.md](../../../../docks/dev/plan.md) | Overall architecture and roadmap |
| [progect_structure.md](../../../../docks/dev/progect_structure.md) | Directory layout and module conventions |
| [data_storage_structure.md](../../../../docks/dev/data_storage_structure.md) | Data models and storage layout |
| [endpoints.md](../../../../docks/dev/endpoints.md) | API contract and route conventions |
| [requirements.md](../../../../docks/dev/requirements.md) | Functional and non-functional requirements |
| [be-conventions.md](./be-conventions.md) | Layered architecture, DI, models, error handling, LLM templates, test patterns |

Also scan the relevant source files to identify:
- Existing utilities, helpers, and base classes that can be reused
- Patterns already in use that may not yet be captured in `be-conventions.md`

### 4. Draft an Implementation Plan

Write a numbered plan. Each step must state:
1. **What** — the specific change (file, function, class, config)
2. **Why** — the motivation tied to the task goal or a convention from the docs
3. **How** — brief description of the approach

Rules during planning:
- **Reuse** existing utils and helpers — do not reinvent
- **Mirror** the patterns already present in the codebase
- **Follow** the code style observed in step 3
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
- Validate after each significant step (import checks, linting where fast)

### 7. Run Tests

```bash
make test-be
```

Always run via `make test-be` from the project root — never run `pytest` directly.

Report results. Fix failures before proceeding. If no tests exist and the task doesn't require them, note this explicitly.

### 8. Request User Review

Before committing, present a summary of all changes made:
- List every file that was created or modified
- Show a `git diff --stat` summary
- Ask the user to review and confirm they are happy with the changes

```bash
git diff --stat
```

Use `vscode_askQuestions` to ask:
> "Please review the diff above. Are you ready to commit and open a PR?"

Do **not** proceed to step 9 until the user explicitly confirms.

If the user requests changes:
- Implement the requested corrections
- Re-run tests if affected
- Re-present the summary and ask for confirmation again

### 9. Commit Changes

```bash
git add -A
git commit -m "<branch-name>: <short imperative summary>"
```

Commit message format: `add-scene-router: wire play endpoint to ScenePlayService`

### 10. Push Branch

```bash
git push -u origin <branch-name>
```

### 11. Open Pull Request

Use the GitHub CLI:
```bash
gh pr create \
  --title "<short summary>" \
  --body "<one-sentence description of changes>

Changes:
- <file or module changed and why>

How to test: <steps>" \
  --base main
```

Include in the PR body:
- Summary of changes made
- How to test / verify

## Completion Checklist

- [ ] `gh` installed and authenticated (`gh auth status` passes)
- [ ] Branch created from up-to-date `main`
- [ ] Task fully read and understood
- [ ] Architecture docs read
- [ ] Plan reviewed and approved by user
- [ ] All plan steps implemented
- [ ] `make test-be` passed (or absence noted)
- [ ] User reviewed changes and approved commit
- [ ] Commit message follows convention
- [ ] Branch pushed
- [ ] PR open with description
