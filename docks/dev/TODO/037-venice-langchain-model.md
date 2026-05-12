# Task 037: Venice LangChain Chat Model

**Feature:** M5 — LLM Adapter
**Status:** TODO

## Description

Implement `VeniceAIChatModel`, a custom LangChain `BaseChatModel` that delegates to `VeniceClient`. This is the LangChain integration layer — it converts LangChain `BaseMessage` lists into Venice API payloads and wraps the response in a `ChatResult`.

## Scope

What IS included:
- `VeniceAIChatModel(BaseChatModel)` class with:
  - Fields: `model: str`, `api_key: str`, `temperature: float = 0`, `max_tokens: int | None = None`
  - `__init__`: initialises `VeniceClient(api_key=self.api_key)`
  - `_llm_type` property returning `"venice-ai"`
  - `_prepare_request_payload(messages)` — converts `BaseMessage` list to Venice payload dict with `venice_parameters: {"include_venice_system_prompt": False}`
  - `_generate(messages, ...)` — sync wrapper calling `loop.run_until_complete(_agenerate(...))`
  - `async _agenerate(messages, ...)` — calls `VeniceClient.chat_complete`, wraps result in `ChatResult`

What is NOT included (deferred):
- Streaming
- Embeddings
- Retry / backoff

## Deliverable

`backend/app/llm/venice_ai.py` — a finished `VeniceAIChatModel` class.

```
backend/app/llm/venice_ai.py
```

## Acceptance Criteria

- [ ] `VeniceAIChatModel(model="...", api_key="...")` constructs without error
- [ ] `_llm_type` returns `"venice-ai"`
- [ ] `_prepare_request_payload` maps `SystemMessage` → `{"role": "system", ...}`, `HumanMessage` → `{"role": "user", ...}`, `AIMessage` → `{"role": "assistant", ...}`
- [ ] `_prepare_request_payload` sets `venice_parameters: {"include_venice_system_prompt": False}`
- [ ] `await _agenerate([...])` returns a `ChatResult` with one `ChatGeneration` whose message content matches the string returned by `VeniceClient.chat_complete`

## Test Notes

Unit test: mock `VeniceClient.chat_complete` to return `"hello"`. Call `await model._agenerate([HumanMessage("hi")])`. Assert `result.generations[0].message.content == "hello"`. Test `_prepare_request_payload` for each message type.

## Dependencies

036
