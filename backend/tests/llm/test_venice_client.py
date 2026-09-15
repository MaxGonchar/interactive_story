from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.exceptions import LLMError
from app.llm.venice_client import VeniceClient, _DEFAULT_TIMEOUT_SECONDS


def test_headers_contain_bearer_token():
    client = VeniceClient(api_key="test-key")
    assert client.headers["Authorization"] == "Bearer test-key"


def test_default_timeout_used_when_env_absent(monkeypatch):
    monkeypatch.delenv("VENICE_TIMEOUT_SECONDS", raising=False)

    client = VeniceClient(api_key="test-key")

    assert client.timeout == _DEFAULT_TIMEOUT_SECONDS


def test_custom_timeout_from_env(monkeypatch):
    monkeypatch.setenv("VENICE_TIMEOUT_SECONDS", "42.5")

    client = VeniceClient(api_key="test-key")

    assert client.timeout == 42.5


def test_invalid_timeout_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("VENICE_TIMEOUT_SECONDS", "not-a-number")

    client = VeniceClient(api_key="test-key")

    assert client.timeout == _DEFAULT_TIMEOUT_SECONDS


def test_non_positive_timeout_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("VENICE_TIMEOUT_SECONDS", "0")

    client = VeniceClient(api_key="test-key")

    assert client.timeout == _DEFAULT_TIMEOUT_SECONDS


def _make_mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.status_code = status_code
    mock_response.raise_for_status = MagicMock()
    return mock_response


@pytest.mark.asyncio
async def test_chat_complete_returns_typed_completion(monkeypatch):
    expected_content = "Once upon a time..."
    fake_response = _make_mock_response(
        {
            "model": "venice-1",
            "created": 1739928524,
            "choices": [{"message": {"content": expected_content}}],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 8,
                "total_tokens": 20,
            },
            "cost": {"usd": 0.00042},
        }
    )
    clock_values = iter([10.0, 11.243])
    monkeypatch.setattr(
        "app.llm.venice_client.time.perf_counter",
        lambda: next(clock_values),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_response
        client = VeniceClient(api_key="test-key")
        result = await client.chat_complete({"model": "venice-1", "messages": []})

    assert result.model_dump() == {
        "content": expected_content,
        "provider_model_id": "venice-1",
        "created": 1739928524,
        "usage": {
            "prompt_tokens": 12,
            "completion_tokens": 8,
            "total_tokens": 20,
        },
        "cost_usd": 0.00042,
        "duration_ms": 1243,
    }
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.args[0] == "https://api.venice.ai/api/v1/chat/completions"


@pytest.mark.asyncio
async def test_chat_complete_allows_missing_cost():
    fake_response = _make_mock_response(
        {
            "model": "venice-1",
            "created": 1739928524,
            "choices": [{"message": {"content": "hello"}}],
            "usage": {
                "prompt_tokens": 1,
                "completion_tokens": 2,
                "total_tokens": 3,
            },
        }
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_response
        client = VeniceClient(api_key="test-key")
        result = await client.chat_complete({"model": "venice-1", "messages": []})

    assert result.cost_usd is None


@pytest.mark.asyncio
async def test_chat_complete_ignores_provider_message_metadata():
    fake_response = _make_mock_response(
        {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1789492728,
            "model": "venice-uncensored-role-play",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "hello",
                        "refusal": None,
                        "annotations": None,
                        "audio": None,
                        "function_call": None,
                        "tool_calls": [],
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 2643,
                "completion_tokens": 81,
                "total_tokens": 2724,
                "prompt_tokens_details": {"cached_tokens": 0},
            },
            "cost": {"usd": 0.0014835, "diem": 0},
            "venice_parameters": {"strip_thinking_response": False},
        }
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_response
        client = VeniceClient(api_key="test-key")
        result = await client.chat_complete({"model": "venice-1", "messages": []})

    assert result.content == "hello"
    assert result.provider_model_id == "venice-uncensored-role-play"
    assert result.cost_usd == 0.0014835


@pytest.mark.asyncio
async def test_chat_complete_raises_llm_error_missing_choices():
    fake_response = _make_mock_response({"result": "ok"})

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_response
        client = VeniceClient(api_key="test-key")
        with pytest.raises(LLMError, match="choices"):
            await client.chat_complete({"model": "venice-1", "messages": []})


@pytest.mark.asyncio
async def test_chat_complete_raises_llm_error_empty_choices():
    fake_response = _make_mock_response({"choices": []})

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_response
        client = VeniceClient(api_key="test-key")
        with pytest.raises(LLMError, match="choices"):
            await client.chat_complete({"model": "venice-1", "messages": []})


@pytest.mark.asyncio
async def test_chat_complete_raises_llm_error_on_non_2xx():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=MagicMock(),
        response=MagicMock(),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        client = VeniceClient(api_key="bad-key")
        with pytest.raises(LLMError):
            await client.chat_complete({"model": "venice-1", "messages": []})
