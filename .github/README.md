# GitHub Copilot Customizations

This directory contains project-specific agents and skills for GitHub Copilot Agent mode.

---

## Agents

Agents are specialized AI modes invoked by name in Copilot Agent mode (e.g. `@agent Bug Review`).

### Bug Review
**File:** `agents/bug-review.agent.md`

Root-cause analysis and fix planning. Does **not** implement fixes — it produces a clear, actionable fix plan.

**Use when:** investigating a bug, diagnosing broken functionality, troubleshooting unexpected behavior, finding root cause.

**How to invoke:**
```
@agent Bug Review <describe the problem or paste a file path>
```

---

### Feature Brainstorm
**File:** `agents/feature-brainstorm.agent.md`

Product and engineering thought partner. Helps think through a feature idea — value, UX, architecture, feasibility — and produces a design doc saved to `docks/dev/features/`.

**Use when:** exploring a new feature idea, discussing technology choices, thinking through UX or architecture, evaluating scope.

**How to invoke:**
```
@agent Feature Brainstorm <describe the feature idea>
```

---

## Skills

Skills are reusable workflows invoked automatically by the default agent based on task description. They can also be referenced explicitly.

### create-tasks
**File:** `skills/create-tasks/SKILL.md`

Decomposes a feature into small, independently-implementable tasks and creates each as a **draft item on the GitHub Project board** (`interactive-story`, project #3, owner `MaxGonchar`).

**Use when:** planning a feature, sprint planning, breaking down work into tickets.

**Example prompt:**
```
Break down the "scene replay" feature into tasks and add them to the board.
```

---

### implement-be-task
**File:** `skills/implement-be-task/SKILL.md`

End-to-end **backend** task implementation workflow: creates a branch, reads the task, produces an implementation plan, writes Python/FastAPI code, runs `make test-be`, and opens a PR.

**Use when:** implementing a backend feature, fix, or refactor — Python, FastAPI, pytest.

**Example prompt:**
```
Implement task "Add scene router" from the project board.
Implement backend task from docks/dev/TODO/011-add-scene-router.md
```

---

### implement-fe-task
**File:** `skills/implement-fe-task/SKILL.md`

End-to-end **frontend** task implementation workflow: creates a branch, reads the task, produces an implementation plan, writes React/Vite code, writes RTL tests (tests are part of done), runs `make test-fe`, and opens a PR.

**Use when:** implementing a frontend feature, fix, or refactor — React components, API modules, pages.

**Example prompt:**
```
Implement task "Add edit button to MessageItem".
Implement frontend task from docks/dev/TODO/025-message-edit.md
```

---

### review-be
**File:** `skills/review-be/SKILL.md`

Reads and reasons about the Python backend code across three dimensions: general anti-patterns, async correctness, and architecture rule violations. Produces a structured report file.

**Use when:** reviewing backend code quality, auditing a module before merging, checking async usage, checking layer/DI conventions.

**Example prompt:**
```
Review the backend code quality.
Review backend code quality for app/services.
```

---

### review-fe
**File:** `skills/review-fe/SKILL.md`

Reads and reasons about the React frontend code across three dimensions: style convention violations (CSS variables, inline styles), React/component anti-patterns (prop drilling, key props, stale closures), and test coverage gaps. Produces a structured report file.

**Use when:** reviewing frontend code quality, checking style convention compliance, auditing component responsibility, finding missing RTL test coverage.

**Example prompt:**
```
Review the frontend code quality.
Review frontend code quality for components/MessageItem.
```

---

### implement-task _(legacy)_
**File:** `skills/implement-task/SKILL.md`

Original unified task implementation skill. Superseded by `implement-be-task` and `implement-fe-task`. Kept for backward compatibility — prefer the split variants for new work.

---

## Tips

- Skills are triggered by the default Copilot agent automatically when the task description matches — you don't need to name the skill explicitly.
- Agents must be invoked by name.
- `copilot-instructions.md` in this directory contains global project context (stack, commands, key docs) that is always injected into every Copilot session.
