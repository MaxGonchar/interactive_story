# Task 073: Forward Message History to LangChain in SceneLLMClient

**Feature:** System prompt correction — multi-turn LLM invocation
**Status:** TODO

## Description

`SceneLLMClient.invoke` currently sends only a `SystemMessage` + a single `HumanMessage` to the LLM, silently discarding all prior conversation turns stored in `context.messages`. This task fixes the method to build a proper multi-turn message chain: `SystemMessage` → alternating `AIMessage`/`HumanMessage` history → `HumanMessage` for the current user input.

The entry-point message (first message in history when `messages[0].role == "assistant"`) should be skipped to avoid duplicating text that already appears in the system prompt's `# Scene Configuration` section.

## Scope

What IS included:
- `backend/app/llm/scene_llm_client.py`: rewrite the `invoke` method to convert `context.messages` to LangChain message objects and insert them between the system message and the current user input
- Import `AIMessage` from `langchain_core.messages` (alongside existing `HumanMessage`, `SystemMessage`)

What is NOT included (deferred):
- Changes to `PromptBuilder` — history is passed as a message chain, not embedded in the system prompt
- Token-budget truncation — out of scope for MVP
- Any changes to test files (covered by task 076)

## Deliverable

Updated `backend/app/llm/scene_llm_client.py` with `invoke` method:

```python
async def invoke(self, context: SceneContext, user_message: str) -> str:
    system_prompt = self._prompt_builder.build_system_prompt(context)
    history_msgs = context.messages
    # Skip the entry-point assistant message (first message, role=assistant)
    # to avoid duplicating text already present in the system prompt.
    if history_msgs and history_msgs[0].role == "assistant":
        history_msgs = history_msgs[1:]
    history = [
        AIMessage(m.content) if m.role == "assistant" else HumanMessage(m.content)
        for m in history_msgs
    ]
    messages = [SystemMessage(system_prompt)] + history + [HumanMessage(user_message)]
    response = await self._model.ainvoke(messages)
    return response.content
```

```
backend/app/llm/scene_llm_client.py
```

## Acceptance Criteria

- [ ] `invoke` sends `SystemMessage` as the first element of the LangChain call
- [ ] All prior turns from `context.messages` (except the entry-point assistant opener) appear between the system message and the current user message, in original order, with correct `AIMessage`/`HumanMessage` types
- [ ] The current user input is always the last message in the chain
- [ ] When `context.messages` is empty the method works identically to before (2-element list: system + user)
- [ ] `AIMessage` is imported from `langchain_core.messages`
- [ ] Existing tests still pass (`pytest backend/tests/llm/test_scene_llm_client.py`)

## Test Notes

Run existing unit tests to confirm no regression:
```
pytest backend/tests/llm/test_scene_llm_client.py -v
```
Full coverage test is added separately in task 076.

## Dependencies

none
