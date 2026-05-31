# Task 076: Test SceneLLMClient Forwards Message History to LangChain

**Feature:** System prompt correction — test coverage
**Status:** TODO

## Description

`test_scene_llm_client.py` currently only exercises the zero-history path (`messages=[]`). After task 073 introduces multi-turn history forwarding, a regression test is needed that verifies: (a) the LangChain model receives the correct total number of message objects, (b) roles are mapped correctly (`assistant` → `AIMessage`, `user` → `HumanMessage`), (c) ordering is `SystemMessage` → history (minus entry-point opener) → `HumanMessage`, and (d) the zero-history path still works.

## Scope

What IS included:
- `backend/tests/llm/test_scene_llm_client.py`: add test(s) covering multi-turn history forwarding
  - Test with non-empty `context.messages` (mix of user and assistant turns after the entry-point opener)
  - Assert `ainvoke` is called with `len(history) + 2` messages (system + filtered history + current user)
  - Assert correct LangChain message types and order
  - Assert entry-point assistant message (first message, `role=="assistant"`) is excluded from the history chain

What is NOT included (deferred):
- Changes to production code (covered by task 073)
- Token-budget or truncation tests — out of MVP scope

## Deliverable

New test function(s) in `backend/tests/llm/test_scene_llm_client.py`:

```python
@pytest.mark.asyncio
async def test_invoke_forwards_message_history(mock_model):
    """Model receives system + filtered history + current user message."""
    context = _make_context(messages=[
        Message(id=1, role="assistant", content="Entry point text"),  # skipped
        Message(id=2, role="user", content="First user turn"),
        Message(id=3, role="assistant", content="First assistant reply"),
    ])
    client = SceneLLMClient(mock_model, PromptBuilder())
    await client.invoke(context, "Second user turn")

    call_args = mock_model.ainvoke.call_args[0][0]
    # system + 2 history (entry-point skipped) + current user = 4 messages
    assert len(call_args) == 4
    assert isinstance(call_args[0], SystemMessage)
    assert isinstance(call_args[1], HumanMessage)   # id=2 user turn
    assert isinstance(call_args[2], AIMessage)      # id=3 assistant reply
    assert isinstance(call_args[3], HumanMessage)   # current user input
    assert call_args[3].content == "Second user turn"


@pytest.mark.asyncio
async def test_invoke_empty_history_sends_two_messages(mock_model):
    """Zero-history context: model still receives exactly system + user."""
    context = _make_context(messages=[])
    client = SceneLLMClient(mock_model, PromptBuilder())
    await client.invoke(context, "Hello")

    call_args = mock_model.ainvoke.call_args[0][0]
    assert len(call_args) == 2
    assert isinstance(call_args[0], SystemMessage)
    assert isinstance(call_args[1], HumanMessage)
```

```
backend/tests/llm/test_scene_llm_client.py
```

## Acceptance Criteria

- [ ] New test `test_invoke_forwards_message_history` passes
- [ ] New test `test_invoke_empty_history_sends_two_messages` passes (or existing equivalent test still passes)
- [ ] Entry-point assistant message (first message with `role=="assistant"`) is verified to be absent from the `ainvoke` call
- [ ] `AIMessage` type is asserted for assistant history turns
- [ ] All tests in the file pass: `pytest backend/tests/llm/test_scene_llm_client.py -v`

## Test Notes

```
pytest backend/tests/llm/test_scene_llm_client.py -v
```

## Dependencies

073
