from __future__ import annotations

import json
import types
from unittest.mock import AsyncMock

import pytest
from langchain_core.exceptions import OutputParserException

from app.llm.summarize_llm_client import SummarizeLLMClient

_SCENE_CONTENT = "The hero entered the cave and defeated the troll."


def _make_client() -> SummarizeLLMClient:
    return SummarizeLLMClient(model=types.SimpleNamespace())


def _ai_response(content: str):
    return types.SimpleNamespace(content=content)


def _well_formed_json(items: list[str] | None = None) -> str:
    return json.dumps({"items": items or ["Hero entered cave.", "Troll was defeated."]})


@pytest.mark.asyncio
async def test_invoke_returns_list_of_strings():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response(_well_formed_json()))
    )
    result = await client.invoke(previous_summary=[], scene_content=_SCENE_CONTENT)
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)
    assert result == ["Hero entered cave.", "Troll was defeated."]


@pytest.mark.asyncio
async def test_invoke_with_empty_previous_summary():
    client = _make_client()
    captured: list[list] = []

    async def _mock_ainvoke(messages):
        captured.append(messages)
        return _ai_response(_well_formed_json())

    client._model = types.SimpleNamespace(ainvoke=_mock_ainvoke)
    await client.invoke(previous_summary=[], scene_content=_SCENE_CONTENT)

    system_msg = captured[0][0].content
    user_msg = captured[0][1].content
    assert "Story So Far" not in system_msg
    assert "Previous Summary" not in user_msg


@pytest.mark.asyncio
async def test_invoke_with_previous_summary():
    client = _make_client()
    captured: list[list] = []

    async def _mock_ainvoke(messages):
        captured.append(messages)
        return _ai_response(_well_formed_json())

    client._model = types.SimpleNamespace(ainvoke=_mock_ainvoke)
    await client.invoke(
        previous_summary=["Earlier, the hero found a map."],
        scene_content=_SCENE_CONTENT,
    )

    system_msg = captured[0][0].content
    user_msg = captured[0][1].content
    assert "Story So Far" in system_msg
    assert "Earlier, the hero found a map." in system_msg
    assert "Earlier, the hero found a map." not in user_msg


@pytest.mark.asyncio
async def test_invoke_raises_on_malformed_response():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response("not valid json at all"))
    )
    with pytest.raises(OutputParserException):
        await client.invoke(previous_summary=[], scene_content=_SCENE_CONTENT)


@pytest.mark.asyncio
async def test_llm_error_propagates():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(side_effect=RuntimeError("LLM unavailable"))
    )
    with pytest.raises(RuntimeError, match="LLM unavailable"):
        await client.invoke(previous_summary=[], scene_content=_SCENE_CONTENT)


@pytest.mark.asyncio
async def test_invoke_raises_on_non_text_response_content():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response([{"type": "text", "text": "hello"}]))
    )

    with pytest.raises(TypeError, match="non-text"):
        await client.invoke(previous_summary=[], scene_content=_SCENE_CONTENT)
