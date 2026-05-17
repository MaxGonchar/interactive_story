# Task 039: Scene LLM Client

**Feature:** M5 — LLM Adapter
**Status:** TODO

## Description

Implement `SceneLLMClient`, the top-level LLM entry point. It assembles the system prompt via `PromptBuilder`, appends the user message, invokes `VeniceAIChatModel`, and returns the assistant reply as a plain string. Model name and API key are read from environment variables.

## Scope

What IS included:
- `SceneLLMClient` class:
  - `__init__(self)` — reads `VENICE_API_KEY` and `VENICE_MODEL` from environment; instantiates `VeniceAIChatModel` and `PromptBuilder`
  - `async invoke(self, context: SceneContext, user_message: str) -> str` — builds system prompt, constructs `[SystemMessage(system_prompt), HumanMessage(user_message)]`, calls `await model.ainvoke(messages)`, returns `response.content`
- `VENICE_MODEL` defaults to `"llama-3.3-70b"` if not set

What is NOT included (deferred):
- Injecting a pre-built model (dependency injection deferred to M6 service layer)
- Message history passed as separate `HumanMessage`/`AIMessage` pairs (history is embedded in the system prompt by `PromptBuilder`)
- Error handling beyond letting exceptions propagate

## Deliverable

`backend/app/llm/scene_llm_client.py` — a finished `SceneLLMClient` class.

```
backend/app/llm/scene_llm_client.py
```

## Acceptance Criteria

- [ ] `SceneLLMClient()` constructs without error when `VENICE_API_KEY` is set in the environment
- [ ] `await client.invoke(context, "Hello")` returns a non-empty string (unit test: mock `VeniceAIChatModel.ainvoke`)
- [ ] `VENICE_MODEL` env var is used as the model name; falls back to `"llama-3.3-70b"` when absent
- [ ] Manual integration test: with a real `VENICE_API_KEY`, `await client.invoke(context, "Hello")` returns a non-empty string from the model

## Test Notes

Unit test: set `VENICE_API_KEY=test` in env, mock `VeniceAIChatModel.ainvoke` to return an `AIMessage("hi")`. Assert `invoke(...)` returns `"hi"`.

Integration test (skipped in CI if `VENICE_API_KEY` is unset): construct a minimal `SceneContext` and call `invoke` against the real API. Assert the result is a non-empty string.

## Dependencies

035, 037, 038
