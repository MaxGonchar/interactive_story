# Task 053: Test SceneLLMClient Raises on Missing VENICE_API_KEY

**Feature:** Absent env configs for LLM adapter
**Status:** TODO

## Description

The `autouse` fixture in `test_scene_llm_client.py` always injects `VENICE_API_KEY`, so there is currently zero test coverage for the missing-key path. A dedicated test using `monkeypatch.delenv` confirms that `SceneLLMClient()` raises a predictable, identifiable exception (not a silent `None` or an unrelated traceback) when the key is absent.

## Scope

What IS included:
- Add one test to `backend/tests/llm/test_scene_llm_client.py` that removes `VENICE_API_KEY` from the environment and asserts that constructing `SceneLLMClient()` raises `KeyError` (current behaviour) or `RuntimeError` (if task 052 is also implemented and the guard is moved into `SceneLLMClient.__init__`)

What is NOT included (deferred):
- Changing `.env.example` (task 051)
- Adding the startup guard in `main.py` (task 052)
- Testing startup-level validation (that would require a separate integration test)

## Deliverable

One new test function in `backend/tests/llm/test_scene_llm_client.py`:

```python
def test_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("VENICE_API_KEY")
    with pytest.raises(KeyError):
        SceneLLMClient()
```

> **Note:** If task 052 moves the key check into `SceneLLMClient.__init__` and converts the exception to `RuntimeError`, update the assertion to `pytest.raises(RuntimeError)` and optionally assert the message contains `"VENICE_API_KEY"`.

```
backend/tests/llm/test_scene_llm_client.py
```

## Acceptance Criteria

- [ ] A test named `test_raises_when_api_key_missing` exists in `test_scene_llm_client.py`
- [ ] The test deletes `VENICE_API_KEY` from the environment via `monkeypatch.delenv`
- [ ] The test asserts the expected exception type is raised when `SceneLLMClient()` is constructed
- [ ] All existing tests in the file continue to pass (`pytest backend/tests/llm/test_scene_llm_client.py`)

## Test Notes

Run: `pytest backend/tests/llm/test_scene_llm_client.py -v`

The existing `autouse` fixture `set_api_key` runs before this test and sets the key. The test must call `monkeypatch.delenv("VENICE_API_KEY")` explicitly to override that fixture and produce the missing-key state.

## Dependencies

none (can be implemented independently; update exception type if task 052 changes it)
