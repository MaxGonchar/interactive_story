# Task 051: Update .env.example with LLM Environment Variables

**Feature:** Absent env configs for LLM adapter
**Status:** TODO

## Description

`.env.example` was authored during M1 before the LLM adapter was introduced in M5. It is missing `VENICE_API_KEY` and `VENICE_MODEL` — the two environment variables consumed by `SceneLLMClient`. Any developer who copies `.env.example` → `.env` will have an incomplete `.env` and hit a `KeyError` on the first `/play` call.

## Scope

What IS included:
- Add `VENICE_API_KEY` entry to `backend/.env.example` with a comment marking it as required
- Add `VENICE_MODEL` entry to `backend/.env.example` with a comment documenting the default value (`llama-3.3-70b`) and marking it as optional

What is NOT included (deferred):
- Changing how `scene_llm_client.py` reads the variables (that is covered in task 052)
- Any test changes

## Deliverable

Updated `backend/.env.example` with two new entries in a dedicated `# LLM / Venice AI` section:

```
backend/.env.example
```

## Acceptance Criteria

- [ ] `VENICE_API_KEY` appears in `backend/.env.example` with a comment that it is required (no default value supplied)
- [ ] `VENICE_MODEL` appears in `backend/.env.example` with a comment that it is optional and defaults to `llama-3.3-70b`
- [ ] Both entries are grouped under a clear section comment (e.g. `# LLM / Venice AI`)
- [ ] Existing entries (`LOG_LEVEL`, `ALLOWED_ORIGINS`, `DATA_DIR`) are unchanged

## Test Notes

Manual verification: open `backend/.env.example` and confirm the two new entries are present with descriptive comments.

## Dependencies

none
