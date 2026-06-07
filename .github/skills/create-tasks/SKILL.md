---
name: create-tasks
description: "Break a feature or requirement into deliverable implementation tasks, present them for review, then create approved tasks as draft items on the GitHub Project board. Use when: planning a feature, creating tasks, writing tasks, breaking down work, sprint planning, task decomposition. Two-phase flow: (1) internally decompose into fine-grained steps, group into shippable tickets, present a review table, wait for approval; (2) compose full task bodies and create board items only after approval."
argument-hint: "Describe the feature and its requirements"
---

# Create Implementation Tasks

## Purpose

Given a feature description and requirements, decompose the work into deliverable, independently-mergeable tickets and create each as a draft item on the GitHub Project board (`interactive-story`, project number **3**, owner `MaxGonchar`).

The flow has two phases:
1. **Plan** — decompose, group, and get the user's approval on the ticket structure.
2. **Create** — compose full task bodies and push to the board.

Never create board items before the user explicitly approves the ticket plan.

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

### Step 2 — Fine-Grained Internal Decomposition

Break the work into the smallest meaningful implementation steps. **This list is internal — do not show it to the user.** Use the typical decomposition orders as guidance:

Typical decomposition order for a backend feature:
1. Pydantic/data models
2. Repository / storage layer
3. Service layer (business logic)
4. Router / endpoint (wiring)
5. Error handling & validation
6. Tests

Typical decomposition order for a frontend feature:
1. API client function (mocked or real)
2. UI component (isolated)
3. Page-level wiring
4. Navigation / routing

### Step 3 — Group Steps into Deliverable Tickets

Merge the fine-grained steps from Step 2 into tickets. Apply this grouping rule to every ticket:

> **After this ticket's PR merges, the system must be in a consistent, working state: no broken tests, no half-wired endpoints, no model changes without the corresponding handler and test updates.**

Practical guidance:
- Changes that must land together to keep the system coherent belong in the same ticket (e.g. a Pydantic model change + the handler that uses it + the test update).
- Changes that are genuinely independent and leave the system working on their own belong in separate tickets.
- Prefer fewer, slightly larger tickets over many tiny ones that individually break the build or tests.

Apply these rules to every ticket:

| Rule | Requirement |
|------|-------------|
| **Shippable** | After the PR merges, the system is in a consistent, working state. No broken tests, no half-wired endpoints. |
| **Focused** | A ticket covers one coherent change — a single feature slice, a self-contained refactor, a complete bug fix. Not an entire feature in one PR. |
| **Testable** | If the change can be unit- or integration-tested, tests are included in the same ticket. |
| **Independent where possible** | Minimise dependencies between tickets. State any unavoidable dependencies explicitly. |

### Step 4 — Present Review Table and Wait for Approval

Before writing full task bodies or creating any board items, present the proposed tickets as a compact table:

| # | Title | Scope (one line) | Depends on |
|---|-------|-----------------|------------|
| 1 | … | … | — |
| 2 | … | … | #1 |

Then explicitly ask the user to approve or request changes. Examples of valid feedback:
- `"merge 2+3"` — combine two tickets into one
- `"split 4 into A (models) and B (endpoint)"` — divide a ticket
- `"drop 5"` — remove a ticket
- `"approved"` / `"looks good"` / `"go ahead"` — proceed to creation

**Do not proceed to Step 5 until the user explicitly approves.**

### Step 5 — Handle Revisions (if requested)

Apply the requested changes to the ticket plan, re-present the updated table, and wait for approval again. Repeat until the user approves.

### Step 6 — Compose Each Task Body

Use the template at [./assets/task-template.md](./assets/task-template.md) as the **body** of each draft item.

Fill in every section. Do not leave placeholder text. Mark sections "N/A" explicitly when not applicable.

The **Motivation** section is mandatory. It must answer: *why do we need these changes?* — the symptom, bug, design gap, or user need that drives the task. If the motivation is already described in `plan.md` or a problem report, summarise it here in 2–4 sentences.

### Step 7 — Create Draft Items on the Board

For each approved ticket, run the following two commands:

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

Before presenting the review table (Step 4), verify each ticket:
- [ ] After this ticket merges, all tests pass and the system behaves correctly
- [ ] Title is concise and action-oriented
- [ ] Scope is one coherent change, not a grab-bag
- [ ] Tests are included in the same ticket as the code they cover
- [ ] Dependencies reference other tickets in this plan by number

Before creating board items (Step 7), additionally verify:
- [ ] Deliverable is a concrete, finished artifact (no vague "implement X")
- [ ] Acceptance criteria are observable and verifiable
- [ ] Dependencies reference real task IDs

## Project Context

- **Stack:** FastAPI (backend) · React (frontend) · LangChain · YAML file storage
- **Plan doc:** `docks/dev/plan.md`
- **Endpoints spec:** `docks/dev/endpoints.md`
- **Requirements:** `docks/dev/requirements.md`
