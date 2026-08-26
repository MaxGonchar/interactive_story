# Feature: Parallel Subagent Backend Code Review (`review-be-parallel`)

**Status**: Draft
**Date**: 2026-08-24

## Summary

An experimental, side-by-side variant of the existing `review-be` skill that replaces its
single-pass, single-context review procedure with an orchestrator/specialist pattern: the
main agent dispatches one isolated-context subagent per review dimension (architecture/DI,
async correctness, general anti-patterns) in parallel, then merges their findings into the
same report format `review-be` already produces. The goal is to test whether isolating each
checklist in its own short-lived context reduces cross-contamination and missed findings
compared to one long-lived context applying all checklists sequentially across every file.

This is a developer-tooling change (a new skill definition), not an application feature —
it has no runtime, API, or data model impact on the Interactive Story product itself.

## Value

**Problem it solves**: In the current `review-be`/`review-fe` skills, one long-lived agent
context reads every file in scope and applies all checklists sequentially. This creates two
risks: (1) attention/recency drift, where files reviewed later in a long session may get
less consistent scrutiny than files reviewed early, and (2) no separation between "finding"
and "judging" — a misapplied rule early in the pass can persist across the rest of the pass
because the same context carries the same (possibly flawed) mental model throughout.

**Fit**: This is internal developer tooling to improve the reliability of an already-adopted
practice (code quality review skills), not a product feature for end users of the
interactive story app.

**Success criteria**:
- Running `review-be-parallel` against the same scope as a prior `review-be` run produces
  at least as many valid findings, with no regressions in finding quality.
- Findings are traceable to a single specialist, making it possible to diagnose and fix one
  specialist's blind spot without touching the others.
- Severity classification stays consistent across specialists (validated by the merge step).

## Scope

**In scope for first iteration**:
- New skill `.github/skills/review-be-parallel/` with its own `SKILL.md`, reused
  `project-rules.md` content, and a `specialists/` directory containing one prompt-spec file
  per dimension: `architecture-specialist.md`, `async-specialist.md`,
  `anti-pattern-specialist.md`.
- Orchestrator procedure: determine scope → read specialist files → dispatch all three via
  `explore_subagent` in parallel, one call per specialist → merge returned findings tables →
  normalize severity → discuss with user → write report (same template/location as
  `review-be`: `docks/dev/quality-reports/be-review-YYYY-MM-DD.md`).
- Distinct, explicit trigger phrasing in the skill's `description` frontmatter so it does not
  compete with `review-be`'s natural-language matching during the trial period.
- Manual side-by-side comparison: run both skills against the same scope and compare reports.

**Out of scope / future**:
- Modifying `review-be` or `review-fe` themselves — they remain untouched during the trial.
- A `review-fe-parallel` counterpart — deferred until the backend trial proves out.
- Further sharding by layer within a dimension (e.g. per-file or per-layer subagents) — the
  dimension-level split (3 specialists) is the only granularity being tested first.
- Automated/tooling-based merge of specialist findings (e.g. a script) — the merge step is
  performed by the orchestrator agent, not external tooling.
- Promoting `review-be-parallel` to replace `review-be` — that decision is deferred until
  after the trial period produces a comparison.

## User Flow

1. User explicitly asks for the experimental review (using distinct phrasing that maps to
   `review-be-parallel`'s description, e.g. "run the parallel/subagent backend review"),
   optionally scoping to a path.
2. Orchestrator resolves scope, reads `project-rules.md` and the three specialist files.
3. Orchestrator dispatches three `explore_subagent` calls in parallel, one per specialist,
   each receiving its own checklist, file scope, and output contract (a findings table only).
4. Orchestrator waits for all three to return, merges the tables, deduplicates overlapping
   findings (keeping the higher severity), and checks severity consistency against the shared
   rubric.
5. Orchestrator presents findings to the user grouped by severity, same as `review-be`
   today, and asks the user to confirm/dismiss/reclassify each one.
6. Orchestrator writes the report to `docks/dev/quality-reports/be-review-YYYY-MM-DD.md`
   (same template as `review-be`).
7. User compares this report against a prior `review-be` run on the same scope to judge
   whether the parallel approach caught more, fewer, or the same findings, and whether
   severity/quality held up.

## API Changes

None — this is an internal developer-tooling skill, not an application-facing change.

## Data Changes

None — no changes to the YAML storage format or application data structures. The only new
files are skill definitions under `.github/skills/review-be-parallel/` and generated review
reports under `docks/dev/quality-reports/`, both of which already exist as a pattern from
`review-be`.

## Backend Changes

None to `backend/app/` — no application code, services, repositories, or models are affected.

## Frontend Changes

None to `frontend/src/` — no components or pages are affected.

## Open Questions

- Does the `explore_subagent` tool run comparable reasoning depth to the main agent context,
  or a lighter-weight pass? Needs empirical validation from the trial, not assumed.
- How should the orchestrator normalize severity when two specialists disagree on the same
  finding, beyond "keep the higher severity"?
- Should specialist files inline their full checklist text (self-contained, isolated context
  needs nothing else) or reference sections of `project-rules.md` (DRY, but requires the
  subagent to read a second file at dispatch time)? Deferred to implementation — leaning
  toward inlining for reliability of the isolated context.
- If the trial succeeds, should `review-be` itself be migrated to this pattern, or should
  both variants coexist permanently (e.g. fast single-pass vs. thorough parallel mode)?
- Should a 4th "test coverage" specialist be added for parity with `review-fe`'s dimensions
  if/when a `review-fe-parallel` variant is built?

## Candidate Specialists

Draft enumeration only — not full prompt specs. Grounded in the existing checklists in
[`review-be/project-rules.md`](../../../.github/skills/review-be/project-rules.md) and
[`implement-fe-task/fe-conventions.md`](../../../.github/skills/implement-fe-task/fe-conventions.md) /
[`frontend_styles_guide.md`](../frontend_styles_guide.md).

### Backend

| Specialist | Scope covered |
|---|---|
| **General anti-patterns** | Section 1 of `project-rules.md`: mutable defaults, broad `except`, `== None`/`== True`, string concat in loops, magic numbers, deep nesting, long functions, unused imports, `print()`, `assert` misuse. Applies to every `.py` file in scope — no layer restriction. |
| **Async correctness** | Section 2: sequential independent `await`s that should be `asyncio.gather`ed, blocking I/O inside `async def`, `asyncio.run()` misuse, unhandled fire-and-forget tasks. Scoped to `app/services/*.py`, `app/repositories/*.py`, `app/llm/*.py` — the only layers with meaningful async logic. |
| **Single responsibility** | Section 3: services touching the filesystem/YAML directly, routers holding business logic, repositories holding domain rules, `SceneLLMClient` doing prompt assembly instead of delegating to `PromptBuilder`, classes/functions with mixed concerns. Needs the full layer map (routers + services + repositories + llm) since it's inherently a cross-layer check. |
| **Dependency injection** | Section 4: constructors building their own dependencies, hard-coded paths/config, missing `get_*` factories in `dependencies.py`, module-level mutable state. Scoped to `app/services/*.py`, `app/repositories/*.py`, `app/api/dependencies.py`. |
| **Storage & API conventions** | Section 5: writes bypassing `atomic_write`, repositories returning raw dicts instead of domain models, inconsistent exception→status-code mapping in routers. Scoped to `app/repositories/*.py` and `app/api/routers/*.py` — the two layers these project-specific rules target. |

Five specialists mirrors the five sections already defined in `project-rules.md`, so no new
checklist content is needed — each specialist just gets one section instead of all five.

### Frontend

| Specialist | Scope covered |
|---|---|
| **Style convention compliance** | Magic values (raw hex/px instead of `var(--token)`), static styles that belong in `index.css` instead of inline, inline `style={{}}` used for non-dynamic values, shared style objects not extracted to `styles.js`, accidental introduction of CSS Modules/styled-components/Tailwind. Scoped to `frontend/src/components/*.jsx`, `frontend/src/pages/*.jsx`, `index.css`, `styles.js`. |
| **React component patterns** | Single responsibility (components mixing fetch + transform + complex render), prop drilling beyond two levels, missing/unstable `key` props, side effects outside `useEffect`, stale closures / missing hook deps, missing loading/error states. Scoped to `frontend/src/components/*.jsx`, `frontend/src/pages/*.jsx`. |
| **Test coverage** | Missing colocated `.test.jsx`/`.test.js` files, tests not covering render/interaction/state-transition/error paths, raw inline test objects instead of `factories.js`, API module tests not mocking `fetch` or not asserting non-ok handling. Scoped to all component/page/API files plus their (absent or present) test siblings — this specialist needs the full file inventory to detect *missing* files, not just content issues in existing ones. |

Three specialists matches `review-fe`'s three existing dimensions one-to-one.

## Risks

- **Loss of cross-cutting context**: an isolated specialist (e.g. async correctness) cannot
  see context another specialist has (e.g. why a service does sequential awaits for DI
  reasons), which could produce false positives that a single-pass reviewer would have
  avoided.
- **Severity calibration drift across specialists**: each subagent scores independently with
  no visibility into the others' findings, risking inconsistent blocking/warning/note
  assignment unless the merge step actively normalizes it.
- **Aggregate cost/latency**: three parallel subagent dispatches, each re-reading
  `project-rules.md` excerpts and their file scope, may cost more in total tool calls/tokens
  than one single-pass run, even though each individual context is smaller and more focused.
- **Skill-matching collision**: if `review-be-parallel`'s description isn't distinct enough
  from `review-be`'s, a generic "review the backend" request could ambiguously match either
  skill during the trial period.
- **Unvalidated assumption about subagent depth**: if `explore_subagent` runs a
  lighter-weight model/pass than the main agent, specialist findings could be shallower than
  the current single-pass review, undermining the whole premise of the experiment.
