---
name: implement-task
description: "Implement changes from a specific task. Use when: implementing a task, working on a ticket, executing a TODO item, starting work on a feature, fixing a bug from a task card. Tasks can be GitHub Project board items or local task files. Produces a feature branch, a reviewed implementation plan, code changes, tests run, and an open PR."
argument-hint: "Title, item ID, or item URL of the board task to implement (e.g. 'Add scene router'); or path to a local task file (e.g. docks/dev/TODO/001-backend-package-layout.md)"
---

# Implement Task

End-to-end workflow for implementing a single task: branch → understand → plan → review → code → test → PR.

## When to Use
- Starting work on any task on the GitHub Project board (`interactive-story`, project **3**, owner `MaxGonchar`)
- Starting work on a local task file in `docks/dev/TODO/`
- Implementing a specific feature, fix, or refactor described in a task
- Executing a ticket when the task title, item ID, or file path is known

## GitHub Project Board

| Field | Value |
|-------|-------|
| Owner | `MaxGonchar` |
| Project number | `3` |
| Project ID | `PVT_kwHOA7xGXs4BX8zb` |
| Status field ID | `PVTSSF_lAHOA7xGXs4BX8zbzhTGDQE` |
| Status option IDs | `f75ad846` = Backlog · `61e4505c` = Ready · `47fc9ee4` = In progress · `df73e18b` = In review · `98236657` = Done |

## Procedure

### 0. Verify GitHub CLI (`gh`)

Before any git or GitHub operation, confirm `gh` is available and authenticated.

Run this check in the terminal:

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

### 1. Locate and Read the Task

Determine the task source:

**A — GitHub Project board item** (preferred)

If given a title or URL, first find the item ID:
```bash
GH_PAGER= gh project item-list 3 --owner MaxGonchar --format json \
  --jq '.items[] | select(.title | test("<search term>"; "i")) | {id, title}'
```

Then fetch the full body (content) of the item:
```bash
GH_PAGER= gh project item-list 3 --owner MaxGonchar --format json \
  --jq '.items[] | select(.id == "<ITEM_ID>") | {id, title, body: .content.body}'
```

Mark the item **In progress** immediately:
```bash
GH_PAGER= gh project item-edit --id <ITEM_ID> \
  --project-id PVT_kwHOA7xGXs4BX8zb \
  --field-id PVTSSF_lAHOA7xGXs4BX8zbzhTGDQE \
  --single-select-option-id 47fc9ee4
```

**B — Local task file**

Read the file directly. If it is in `docks/dev/TODO/`, move it to `docks/dev/IN_PROGRESS/`:
```bash
mv docks/dev/TODO/<task-file>.md docks/dev/IN_PROGRESS/<task-file>.md
```

From either source, extract:
- **Goal**: what problem this solves or feature it delivers
- **Scope**: which files/modules are touched
- **Deliverable**: the concrete artifact to produce
- **Acceptance criteria**: the conditions for "done"
- **Test notes**: what to verify

### 2. Create and Switch to Branch

Determine the branch name from the task title — derive 2–4 words in kebab-case (e.g. `add-scene-router`):

```bash
gh repo sync          # sync local main with remote
git checkout main
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

Also scan the relevant source files to identify:
- Existing utilities, helpers, and base classes that can be reused
- Patterns already in use (error handling, response shapes, naming conventions)
- Style (import order, type annotations, docstring style, test structure)

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

If tests exist or the task specifies them:
```bash
# Adjust to the project's actual test command
pytest          # backend
# or
npm test        # frontend
```

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

`gh` manages authentication, so no separate credential setup is needed:

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

How to test: <steps>

Board item: <ITEM_ID or task title>" \
  --base main
```

Include in the PR body:
- Reference to the board item title (or local task file path)
- Summary of changes made
- How to test / verify

### 12. Mark Board Item Done

If the task came from the GitHub Project board, set its status to **Done**:
```bash
GH_PAGER= gh project item-edit --id <ITEM_ID> \
  --project-id PVT_kwHOA7xGXs4BX8zb \
  --field-id PVTSSF_lAHOA7xGXs4BX8zbzhTGDQE \
  --single-select-option-id 98236657
```

If the task came from a local file, move it to `docks/dev/DONE/`:
```bash
mv docks/dev/IN_PROGRESS/<task-file>.md docks/dev/DONE/<task-file>.md
```

## Completion Checklist

- [ ] `gh` installed and authenticated (`gh auth status` passes)
- [ ] Task located (board item fetched or local file read)
- [ ] Board item (or local file) marked **In progress**
- [ ] Branch created from up-to-date `main`
- [ ] Task fully read and understood
- [ ] Architecture docs read
- [ ] Plan reviewed and approved by user
- [ ] All plan steps implemented
- [ ] Tests passed (or absence noted)
- [ ] User reviewed changes and approved commit
- [ ] Commit message follows convention
- [ ] Branch pushed
- [ ] PR open with description
- [ ] Board item marked **Done** (or local file moved to `DONE/`)
