import os
from unittest.mock import AsyncMock, patch

import pytest

import types
from app.llm.models import SceneContext
from app.llm.scene_llm_client import SceneLLMClient, _DEFAULT_MODEL
from app.models.domain import SceneDescription, Message
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


def _make_context() -> SceneContext:
    return SceneContext(
        scene_description=SceneDescription(
            entry_point="A dark alley.",
            general_scene_guide="Build tension.",
            writing_style="Gritty noir.",
        ),
        characters=[],
        messages=[],
    )


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def clear_model_env(monkeypatch):
    monkeypatch.delenv("VENICE_MODEL", raising=False)


@pytest.mark.asyncio
async def test_invoke_returns_model_content():
    client = SceneLLMClient()
    with patch.object(client._model._client, "chat_complete", new_callable=AsyncMock) as mock_cc:
        mock_cc.return_value = "hi"
        result = await client.invoke(_make_context(), "Hello")
    assert result == "hi"
    mock_cc.assert_called_once()


def test_default_model_name_used_when_env_absent():
    client = SceneLLMClient()
    assert client._model.model == _DEFAULT_MODEL


def test_custom_model_name_from_env(monkeypatch):
    monkeypatch.setenv("VENICE_MODEL", "my-custom-model")
    client = SceneLLMClient()
    assert client._model.model == "my-custom-model"


def test_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("VENICE_API_KEY", raising=False)
    with pytest.raises(KeyError):
        SceneLLMClient()


def _make_context_with_messages(messages):
    return SceneContext(
        scene_description=SceneDescription(
            entry_point="A dark alley.",
            general_scene_guide="Build tension.",
            writing_style="Gritty noir.",
        ),
        characters=[],
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
    client._prompt_builder = SceneLLMClient()._prompt_builder
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
    client._prompt_builder = SceneLLMClient()._prompt_builder
    await client.invoke(context, "Hello")
    call_args = mock_model.ainvoke.call_args[0][0]
    assert len(call_args) == 2
    assert isinstance(call_args[0], SystemMessage)
    assert isinstance(call_args[1], HumanMessage)
