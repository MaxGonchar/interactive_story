---
name: implement-task
description: "Implement changes from a specific task file. Use when: implementing a task, working on a ticket, executing a TODO item, starting work on a feature, fixing a bug from a task card. Produces a feature branch, a reviewed implementation plan, code changes, tests run, and an open PR."
argument-hint: "Path or ID of the task file to implement, e.g. docks/dev/TODO/001-backend-package-layout.md"
---

# Implement Task

End-to-end workflow for implementing a single task: branch → understand → plan → review → code → test → PR.

## When to Use
- Starting work on any task in `docks/dev/TODO/`
- Implementing a specific feature, fix, or refactor described in a task file
- Executing a ticket when the task ID or path is known

## Procedure

### 1. Create and Switch to Branch

Determine the branch name:
- If the task file has a numeric ID prefix (e.g. `001-backend-package-layout.md`), use the full slug: `001-backend-package-layout`
- Otherwise derive 2–4 words from the task title in kebab-case

```bash
git checkout main && git pull
git checkout -b <branch-name>
```

### 2. Understand the Task

Read the task file in full. Extract:
- **Goal**: what problem this solves or feature it delivers
- **Scope**: which files/modules are touched
- **Deliverable**: the concrete artifact to produce
- **Acceptance criteria**: the conditions for "done"
- **Test notes**: what to verify

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

### 8. Commit Changes

```bash
git add -A
git commit -m "<task-id>: <short imperative summary>"
```

Commit message format: `001: add FastAPI health-check endpoint`

### 9. Push Branch

```bash
git push -u origin <branch-name>
```

### 10. Open Pull Request

Use the GitHub CLI or GitKraken MCP tool:
```bash
gh pr create \
  --title "<task-id>: <short summary>" \
  --body "Closes task <task-id>. <one-sentence description of changes>" \
  --base main
```

Include in the PR body:
- Reference to the task file
- Summary of changes made
- How to test / verify

## Completion Checklist

- [ ] Branch created from up-to-date `main`
- [ ] Task fully read and understood
- [ ] Architecture docs read
- [ ] Plan reviewed and approved by user
- [ ] All plan steps implemented
- [ ] Tests passed (or absence noted)
- [ ] Commit message follows convention
- [ ] Branch pushed
- [ ] PR open with description
