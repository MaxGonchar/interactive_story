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

### implement-task
**File:** `skills/implement-task/SKILL.md`

End-to-end task implementation workflow: creates a branch, reads the task, produces an implementation plan, writes code, runs tests, and opens a PR.

**Use when:** starting work on a board task or a local task file in `docks/dev/TODO/`.

**Example prompt:**
```
Implement task "Add scene router" from the project board.
Implement task from docks/dev/TODO/011-add-scene-router.md
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

## Tips

- Skills are triggered by the default Copilot agent automatically when the task description matches — you don't need to name the skill explicitly.
- Agents must be invoked by name.
- `copilot-instructions.md` in this directory contains global project context (stack, commands, key docs) that is always injected into every Copilot session.
