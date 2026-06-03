---
name: create-tasks
description: "Break a feature or requirement into small, reviewable implementation tasks and create each as a draft item on the GitHub Project board. Use when: planning a feature, creating tasks, writing tasks, breaking down work, sprint planning, task decomposition. Produces one draft item per task using a consistent template with description, motivation (why the change is needed), scope, deliverable, acceptance criteria, and test notes."
argument-hint: "Describe the feature and its requirements"
---

# Create Implementation Tasks

## Purpose

Given a feature description and requirements, decompose the work into small, independently-implementable tasks and create each as a draft item on the GitHub Project board (`interactive-story`, project number **3**, owner `MaxGonchar`).

## GitHub Project Board

| Field | Value |
|-------|-------|
| Owner | `MaxGonchar` |
| Project number | `3` |
| Project ID | `PVT_kwHOA7xGXs4BX8zb` |
| Status field ID | `PVTSSF_lAHOA7xGXs4BX8zbzhTGDQE` |
| Default status | `Backlog` (option ID `f75ad846`) |

Tasks are created as **draft items** (no linked issue/PR). Each draft item has a **Title** and a **Body** containing the full task detail.

## Procedure

### Step 1 — Understand the Feature

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
| **One item per task** | Each task gets its own board item. Do not bundle multiple unrelated changes. |

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

### Step 4 — Compose Each Task Body

Use the template at [./assets/task-template.md](./assets/task-template.md) as the **body** of the draft item.

Fill in every section. Do not leave placeholder text. Mark sections "N/A" explicitly when not applicable.

The **Motivation** section is mandatory. It must answer: *why do we need these changes?* — the symptom, bug, design gap, or user need that drives the task. If the motivation is already described in `plan.md` or a problem report, summarise it here in 2–4 sentences.

### Step 5 — Create Draft Items on the Board

For each task, run the following two commands:

**1. Create the draft item and capture its ID:**
```bash
ITEM_ID=$(gh project item-create 3 --owner MaxGonchar \
  --title "<task title>" \
  --body "<task body markdown>" \
  --format json --jq '.id')
```

**2. Set the Status to `Backlog`:**
```bash
gh project item-edit --id "$ITEM_ID" \
  --project-id PVT_kwHOA7xGXs4BX8zb \
  --field-id PVTSSF_lAHOA7xGXs4BX8zbzhTGDQE \
  --single-select-option-id f75ad846
```

After all items are created, print a summary listing each task title and its item ID.

## Quality Checklist

Before finishing, verify each task:
- [ ] Title is concise and action-oriented
- [ ] Deliverable is a concrete, finished artifact (no vague "implement X")
- [ ] Acceptance criteria are observable and verifiable
- [ ] Dependencies reference real task IDs
- [ ] Scope section explicitly lists what is OUT of scope

## Project Context

- **Stack:** FastAPI (backend) · React (frontend) · LangChain · YAML file storage
- **Plan doc:** `docks/dev/plan.md`
- **Endpoints spec:** `docks/dev/endpoints.md`
- **Requirements:** `docks/dev/requirements.md`
