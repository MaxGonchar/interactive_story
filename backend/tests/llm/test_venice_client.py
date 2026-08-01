from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.exceptions import LLMError
from app.llm.venice_client import VeniceClient


def test_headers_contain_bearer_token():
    client = VeniceClient(api_key="test-key")
    assert client.headers["Authorization"] == "Bearer test-key"


def _make_mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.status_code = status_code
    mock_response.raise_for_status = MagicMock()
    return mock_response


@pytest.mark.asyncio
async def test_chat_complete_returns_content():
    expected_content = "Once upon a time..."
    fake_response = _make_mock_response(
        {"choices": [{"message": {"content": expected_content}}]}
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = fake_response
        client = VeniceClient(api_key="test-key")
        result = await client.chat_complete({"model": "venice-1", "messages": []})

    assert result == expected_content
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.args[0] == "https://api.venice.ai/api/v1/chat/completions"


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
