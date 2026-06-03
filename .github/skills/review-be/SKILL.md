---
name: review-be
description: "Review backend Python code quality. Use when: reviewing backend code, checking code quality, scanning for anti-patterns, checking async usage, checking single responsibility, checking dependency injection, auditing Python practices, code review, quality report."
argument-hint: "Optional: specific module or path to review (e.g. 'app/services' or 'all'). Defaults to full backend."
---

# Backend Python Code Review

## Purpose

Scan the Python backend for quality issues across three dimensions:

1. **General Python anti-patterns and bad practices**
2. **Async correctness** — sequential `await` chains that should be parallelized
3. **Architecture rules** — single responsibility, dependency injection, and project-specific layer conventions

No third-party tools (linters, mypy, coverage). Pure code reading and reasoning.

At the end: discuss findings with the user, then produce a structured report file.

---

## Procedure

### Step 1 — Determine scope

If the user specified a path, restrict the review to that module. Otherwise review the full `backend/app/` tree.

Start by reading the layer conventions in [project-rules.md](./project-rules.md) and in `docks/dev/progect_structure.md`. These define what is *expected* — violations are findings.

### Step 2 — Collect source files

List all `.py` files under the target scope. Group them by layer:

| Layer | Path pattern |
|---|---|
| API / Routers | `app/api/routers/*.py`, `app/api/dependencies.py` |
| Services | `app/services/*.py` |
| Repositories | `app/repositories/*.py` |
| LLM adapter | `app/llm/*.py` |
| Models | `app/models/*.py` |
| Utils | `app/utils/*.py` |

### Step 3 — Run the checklist

Read each file and apply all checks from [project-rules.md](./project-rules.md).

For every finding record:

| Field | Content |
|---|---|
| **File** | Relative path |
| **Line(s)** | Approximate line range |
| **Rule** | Which check was triggered |
| **Severity** | `blocking` / `warning` / `note` |
| **Evidence** | Exact code snippet |
| **Fix** | Concrete suggestion |

### Step 4 — Discuss with the user

Present findings **grouped by severity**, then by layer. For each finding:
- Briefly explain *why* it matters
- Show the evidence snippet
- Propose a fix

Ask the user to confirm, dismiss, or reclassify each finding before writing the report. Questions to ask:
- "Is this intentional? Should I mark it as accepted?"
- "Is this out of scope for now?"

### Step 5 — Write the report

After discussion, create the report file at:

```
docks/dev/quality-reports/be-review-YYYY-MM-DD.md
```

Use the [report template](#report-template) below. Include only findings that were confirmed or left unresolved. Mark dismissed items as **Accepted / Won't fix** with the user's reason.

---

## Report Template

```markdown
# Backend Code Quality Report — YYYY-MM-DD

## Summary

| Severity | Count |
|---|---|
| Blocking | N |
| Warning | N |
| Note | N |
| Accepted / Won't fix | N |

---

## Blocking

### [FILE:LINE] Rule name
**Evidence**
```python
# snippet
```
**Fix**: ...

---

## Warning

...

---

## Note

...

---

## Accepted / Won't fix

| File | Rule | Reason |
|---|---|---|
| ... | ... | ... |
```

---

## Severity Guide

| Level | Meaning |
|---|---|
| `blocking` | Correctness risk, data loss, security hole, or broken contract — must fix before merge |
| `warning` | Maintainability or reliability degradation — should fix soon |
| `note` | Style, minor smell, or improvement opportunity — fix when touching the code |
