import types
from unittest.mock import AsyncMock

import pytest

from app.llm.story_engine_client import StoryEngineClient, _DEFAULT_MODEL
from app.models.domain import CharacterCard

DEFAULT_CHARACTER = CharacterCard(id="c-1", name="Aria")


def _make_client() -> StoryEngineClient:
    return StoryEngineClient(
        characters=[DEFAULT_CHARACTER],
        writing_style="Dark and atmospheric.",
    )


def _ai_response(content: str):
    return types.SimpleNamespace(content=content)


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def clear_model_env(monkeypatch):
    monkeypatch.delenv("VENICE_MODEL", raising=False)


@pytest.mark.asyncio
async def test_invoke_returns_llm_content():
    client = _make_client()
    expected = "The ruins loomed ahead, shadows dancing at the threshold."
    mock_ainvoke = AsyncMock(return_value=_ai_response(expected))
    client._model = types.SimpleNamespace(ainvoke=mock_ainvoke)
    result = await client.invoke(
        story_text="You approach the ruins.",
        action="Step inside",
        consequence="The darkness swallows you.",
    )
    assert result == expected
    mock_ainvoke.assert_called_once()


def test_default_model_used_when_env_absent():
    client = _make_client()
    assert client._model.model == _DEFAULT_MODEL


def test_custom_model_from_env(monkeypatch):
    monkeypatch.setenv("VENICE_MODEL", "my-custom-model")
    client = _make_client()
    assert client._model.model == "my-custom-model"


def test_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("VENICE_API_KEY", raising=False)
    with pytest.raises(KeyError):
        _make_client()
