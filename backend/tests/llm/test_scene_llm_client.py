from __future__ import annotations

import logging
import types
from unittest.mock import AsyncMock

import pytest
from app.llm.models import SceneContext
from app.llm.scene_llm_client import SceneLLMClient
from app.models.domain import CharacterCard, SceneDescription, Message
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


DEFAULT_USER_CHARACTER = CharacterCard(id="user-1", story_id="story-1", name="Emma")


def _make_context() -> SceneContext:
    return SceneContext(
        scene_description=SceneDescription(
            general_scene_guide="Build tension.",
            writing_style="Gritty noir.",
        ),
        characters=[],
        user_character=DEFAULT_USER_CHARACTER,
        messages=[],
    )


def _make_client() -> SceneLLMClient:
    return SceneLLMClient(model=types.SimpleNamespace(ainvoke=AsyncMock()))


@pytest.mark.asyncio
async def test_invoke_returns_model_content():
    client = _make_client()
    client._model.ainvoke.return_value = types.SimpleNamespace(content="hi")
    result = await client.invoke(_make_context(), "Hello")
    assert result == "hi"
    client._model.ainvoke.assert_called_once()


def _make_context_with_messages(messages):
    return SceneContext(
        scene_description=SceneDescription(
            general_scene_guide="Build tension.",
            writing_style="Gritty noir.",
        ),
        characters=[],
        user_character=DEFAULT_USER_CHARACTER,
        messages=messages,
    )


@pytest.mark.asyncio
async def test_invoke_forwards_all_message_history(monkeypatch):
    # Prepare mock model with ainvoke
    mock_model = types.SimpleNamespace()
    mock_model.ainvoke = AsyncMock(return_value=types.SimpleNamespace(content="response"))
    # Messages: entry-point assistant, user, assistant
    messages = [
        Message(id=1, role="assistant", content="Entry point text"),
        Message(id=2, role="user", content="First user turn"),
        Message(id=3, role="assistant", content="First assistant reply"),
    ]
    context = _make_context_with_messages(messages)
    client = SceneLLMClient.__new__(SceneLLMClient)
    client._model = mock_model
    client._prompt_builder = _make_client()._prompt_builder
    client._logger = logging.getLogger("test.scene_llm_client")
    await client.invoke(context, "Second user turn")
    call_args = mock_model.ainvoke.call_args[0][0]
    # system + 3 history + current user = 5 messages
    assert len(call_args) == 5
    assert isinstance(call_args[0], SystemMessage)
    assert isinstance(call_args[1], AIMessage)      # id=1 assistant
    assert call_args[1].content == "Entry point text"
    assert isinstance(call_args[2], HumanMessage)   # id=2 user turn
    assert call_args[2].content == "First user turn"
    assert isinstance(call_args[3], AIMessage)      # id=3 assistant reply
    assert call_args[3].content == "First assistant reply"
    assert isinstance(call_args[4], HumanMessage)   # current user input
    assert call_args[4].content == "Second user turn"

@pytest.mark.asyncio
async def test_invoke_empty_history_sends_two_messages(monkeypatch):
    mock_model = types.SimpleNamespace()
    mock_model.ainvoke = AsyncMock(return_value=types.SimpleNamespace(content="response"))
    context = _make_context_with_messages([])
    client = SceneLLMClient.__new__(SceneLLMClient)
    client._model = mock_model
    client._prompt_builder = _make_client()._prompt_builder
    client._logger = logging.getLogger("test.scene_llm_client")
    await client.invoke(context, "Hello")
    call_args = mock_model.ainvoke.call_args[0][0]
    assert len(call_args) == 2
    assert isinstance(call_args[0], SystemMessage)
    assert isinstance(call_args[1], HumanMessage)
