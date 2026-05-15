from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.llm.venice_ai import VeniceAIChatModel


def _make_model() -> VeniceAIChatModel:
    return VeniceAIChatModel(model="venice-1", api_key="test-key")


def test_llm_type():
    assert _make_model()._llm_type == "venice-ai"


def test_prepare_payload_human_message():
    model = _make_model()
    payload = model._prepare_request_payload([HumanMessage(content="hi")])
    assert payload["messages"] == [{"role": "user", "content": "hi"}]


def test_prepare_payload_system_message():
    model = _make_model()
    payload = model._prepare_request_payload([SystemMessage(content="You are helpful.")])
    assert payload["messages"] == [{"role": "system", "content": "You are helpful."}]


def test_prepare_payload_ai_message():
    model = _make_model()
    payload = model._prepare_request_payload([AIMessage(content="Sure!")])
    assert payload["messages"] == [{"role": "assistant", "content": "Sure!"}]


def test_prepare_payload_venice_parameters():
    model = _make_model()
    payload = model._prepare_request_payload([HumanMessage(content="hi")])
    assert payload["venice_parameters"] == {"include_venice_system_prompt": False}


def test_prepare_payload_unknown_message_type_raises():
    from langchain_core.messages import BaseMessage

    class UnknownMessage(BaseMessage):
        type: str = "unknown"

    model = _make_model()
    with pytest.raises(ValueError, match="Unsupported message type"):
        model._prepare_request_payload([UnknownMessage(content="?")])


@pytest.mark.asyncio
async def test_agenerate_returns_chat_result():
    model = _make_model()
    with patch.object(model._client, "chat_complete", new_callable=AsyncMock) as mock_cc:
        mock_cc.return_value = "hello"
        result = await model._agenerate([HumanMessage(content="hi")])

    assert len(result.generations) == 1
    assert result.generations[0].message.content == "hello"
    mock_cc.assert_called_once()
