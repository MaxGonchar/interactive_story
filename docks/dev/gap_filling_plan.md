# Gap Filling Plan (Pre-Implementation)

## Goal
Prepare complete and consistent project documentation before implementation starts.

This plan closes all critical gaps across:
- requirements
- API contract
- data storage/schema
- architecture structure
- implementation roadmap

## How We Work
- We move step by step.
- Each step ends with a review checkpoint.
- We only proceed after confirmation.
- We track status directly in this file.

## Scope of This Plan
In scope:
- docs in `docks/dev/`
- MVP boundary definition
- implementation-ready contracts and structure

Out of scope:
- coding backend/frontend
- infrastructure/deployment setup
- post-MVP feature implementation

## Step-by-Step Execution

### Step 1 - Lock MVP Scope and Definitions
Status: COMPLETED

Target file:
- `docks/dev/requirements.md`

What we will do:
- Define exact MVP and out-of-scope features.
- Align scope with existing diagram ideas.
- Add domain definitions: Story, Scene, Message, finished scene state.
- Add measurable non-functional baseline for MVP.

Done criteria:
- No ambiguity about what is/is not in MVP.
- Requirements can be mapped directly to API and data model.

Review checkpoint:
- Confirm MVP boundary and terminology.

---

### Step 2 - Define Data Storage and YAML Schemas
Status: COMPLETED

Target file:
- `docks/dev/data_storage_structure.md`

What we will do:
- Define filesystem layout under data directory.
- Define YAML schema for stories/scenes/messages.
- Define ID rules (UUID/int where applicable).
- Define write strategy (atomic write), update rules, and consistency invariants.

Done criteria:
- Repository layer can be implemented without open schema questions.
- Every API resource has a storage mapping.

Review checkpoint:
- Confirm schema fields and storage lifecycle.

---

### Step 3 - Finalize MVP API Contract
Status: COMPLETED

Target file:
- `docks/dev/endpoints.md`

What we will do:
- Keep only MVP endpoints (or explicitly mark post-MVP endpoints).
- Fix JSON examples and request/response consistency.
- Define status codes and standard error response model.
- Define validation rules and ordering semantics.

Done criteria:
- Backend handlers can be implemented directly from this spec.
- Frontend can integrate without contract ambiguity.

Review checkpoint:
- Confirm endpoint list and payload formats.

---

### Step 4 - Finalize Project Architecture Structure
Status: COMPLETED

Target file:
- `docks/dev/progect_structure.md`

What we will do:
- Convert open questions into final decisions.
- Define BE layers and module boundaries (API, services, repositories, LLM adapter, utils).
- Define FE structure (pages, API client, components, state boundaries).
- Add one request-flow example for "play scene".

Done criteria:
- Team can create project skeleton with clear module ownership.
- No unresolved architecture-level questions remain for MVP.

Review checkpoint:
- Confirm architecture choices and boundaries.

---

### Step 5 - Rebuild Implementation Plan with Milestones
Status: IN REVIEW

Target file:
- `docks/dev/plan.md`

What we will do:
- Rewrite plan into milestones with entry/exit criteria.
- Add dependencies between milestones.
- Add test gates and quality checks per milestone.
- Separate MVP delivery and post-MVP roadmap.

Done criteria:
- Plan is executable and trackable.
- Each milestone has clear completion conditions.

Review checkpoint:
- Confirm sequence and delivery expectations.

---

## Tracking Board
- [x] Step 1 completed
- [x] Step 2 completed
- [x] Step 3 completed
- [x] Step 4 completed
- [ ] Step 5 completed

## Change Log
- 2026-05-02: Initial gap-filling plan created.
- 2026-05-02: Step 1 drafted in requirements and moved to review.
- 2026-05-02: Step 1 approved and marked completed. Step 2 started.
- 2026-05-02: Step 2 expanded with object model fields (story characters, scene character subset, scene description, finished scene summary).
- 2026-05-02: Step 2 storage model revised to separate character files and split scene metadata/messages files.
- 2026-05-02: Step 2 approved and marked completed. Step 3 started.
- 2026-05-02: Step 3 approved and marked completed. Step 4 started.
- 2026-05-02: Step 4 approved and marked completed. Step 5 started.
- 2026-05-02: Step 5 drafted in plan.v2.md and moved to review.
- 2026-05-02: Step 3 endpoints.md rewritten — MVP endpoints, error model, status codes, and message edit/delete added to MVP scope.
- 2026-05-02: Step 3 approved and marked completed. Step 4 architecture draft created.

## Current Focus
Step 4 - Finalize Project Architecture Structure
