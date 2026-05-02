---
name: create-tasks
description: "Break a feature or requirement into small, reviewable implementation tasks and save each as a markdown file in the project TODO folder. Use when: planning a feature, creating tasks, writing tasks, breaking down work, sprint planning, task decomposition. Produces one .md file per task using a consistent template with id, description, scope, deliverable, acceptance criteria, and test notes."
argument-hint: "Describe the feature and its requirements"
---

# Create Implementation Tasks

## Purpose

Given a feature description and requirements, decompose the work into small, independently-implementable tasks and save each as a markdown file in the project TODO folder.

## Task Storage

| State | Folder |
|-------|--------|
| New | `docks/dev/TODO/` |
| In progress | `docks/dev/IN PROGRESS/` |
| Finished | `docks/dev/DONE/` |

## Task File Naming

`{id}-{short-name}.md`

- `id`: zero-padded 3-digit integer (`001`, `002`, …), globally incremental across all three folders
- `short-name`: 2–5 words joined with hyphens, lowercase (e.g., `create-story-model`)

Example: `007-add-scene-router.md`

## Procedure

### Step 1 — Determine Next ID

Scan all three task folders (`TODO/`, `IN PROGRESS/`, `DONE/`) for existing task files. Extract the highest numeric ID from the filenames. Next ID = max + 1, zero-padded to 3 digits. If no tasks exist, start at `001`.

### Step 2 — Understand the Feature

Read the feature description and requirements carefully. Identify:
- The data models / schemas involved
- The backend endpoints or services needed
- The frontend components or pages needed
- Any configuration, migrations, or scripts needed
- Integration or wiring tasks (connecting pieces together)

### Step 3 — Decompose into Tasks

Apply these rules to every task:

| Rule | Requirement |
|------|-------------|
| **Small** | A task should be reviewable in one focused PR. A single class, function, endpoint, or component per task. No "implement the whole feature" tasks. |
| **Finished deliverable** | The artifact must be complete in isolation: a working class/function, a component skeleton that renders, an endpoint that returns hardcoded data, a migration that runs. No half-implementations. |
| **Testable** | If the deliverable can be unit- or integration-tested, state it explicitly in Acceptance Criteria. If only manual testing applies, describe the exact steps. |
| **Independent where possible** | Minimize dependencies between tasks. State dependencies explicitly. |
| **One file per task** | Each task gets its own markdown file. Do not bundle multiple unrelated changes. |

Typical decomposition order for a backend feature:
1. Pydantic/data models
2. Repository / storage layer
3. Service layer (business logic)
4. Router / endpoint (wiring)
5. Error handling & validation

Typical decomposition order for a frontend feature:
1. API client function (mocked or real)
2. UI component (isolated)
3. Page-level wiring
4. Navigation / routing

### Step 4 — Write Each Task File

Use the template at [./assets/task-template.md](./assets/task-template.md).

Fill in every section. Do not leave placeholder text. Mark sections "N/A" explicitly when not applicable.

### Step 5 — Save Files

Save each task file to `docks/dev/TODO/{id}-{short-name}.md`.

After saving, list all created task files with their IDs and one-line descriptions as a summary.

## Quality Checklist

Before finishing, verify each task:
- [ ] Filename matches `{id}-{short-name}.md` pattern
- [ ] ID is globally unique (no collision with existing files)
- [ ] Deliverable is a concrete, finished artifact (no vague "implement X")
- [ ] Acceptance criteria are observable and verifiable
- [ ] Dependencies reference real task IDs
- [ ] Scope section explicitly lists what is OUT of scope

## Project Context

- **Stack:** FastAPI (backend) · React (frontend) · LangChain · YAML file storage
- **Plan doc:** `docks/dev/plan.md`
- **Endpoints spec:** `docks/dev/endpoints.md`
- **Requirements:** `docks/dev/requirements.md`
