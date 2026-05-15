# Task 036: Venice HTTP Client

**Feature:** M5 — LLM Adapter
**Status:** TODO

## Description

Implement a low-level async HTTP client for the Venice AI chat completions API. Handles authentication, request construction, response parsing, and error mapping. This is the only place in the codebase that talks to Venice AI directly.

## Scope

What IS included:
- `VeniceClient` class:
  - `__init__(self, api_key: str)` — stores key, sets `base_url = "https://api.venice.ai/api/v1"`, `timeout = 60.0`
  - `async chat_complete(self, payload: dict) -> str` — POSTs to `/chat/completions`, returns `choices[0].message.content`; raises `httpx.HTTPStatusError` on non-2xx; raises `ValueError` if response shape is unexpected
- `httpx.AsyncClient` used for all HTTP calls

What is NOT included (deferred):
- Embeddings endpoint
- Retry logic
- Streaming responses
- Logging

## Deliverable

`backend/app/llm/venice_client.py` — a finished `VeniceClient` class.

```
backend/app/llm/venice_client.py
```

## Acceptance Criteria

- [ ] `VeniceClient(api_key="test").headers` returns a dict with `"Authorization": "Bearer test"`
- [ ] `chat_complete` sends a POST to `https://api.venice.ai/api/v1/chat/completions` with the given payload
- [ ] `chat_complete` returns `choices[0].message.content` from the response JSON
- [ ] `chat_complete` raises `ValueError` if `choices` is missing or empty in the response

## Test Notes

Unit test with `unittest.mock` or `pytest-mock`: patch `httpx.AsyncClient.post` to return a fake response dict. Assert the returned string matches `choices[0].message.content`. Test the `ValueError` path with a malformed response.

## Dependencies

none
