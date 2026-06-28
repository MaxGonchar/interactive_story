import json
import types
from unittest.mock import AsyncMock

import pytest
from langchain_core.exceptions import OutputParserException

from app.llm.choice_engine_client import ChoiceEngineClient, _DEFAULT_MODEL
from app.models.domain import CharacterCard, Choice

DEFAULT_CHARACTER = CharacterCard(id="c-1", story_id="s-1", name="Aria")


def _make_client() -> ChoiceEngineClient:
    return ChoiceEngineClient(
        plot_direction="Head toward the ancient ruins.",
        characters=[DEFAULT_CHARACTER],
    )


def _ai_response(content: str):
    return types.SimpleNamespace(content=content)


def _well_formed_json() -> str:
    return json.dumps(
        {
            "options": [
                {"action": "Sneak past the guards", "consequence": "You slip through undetected."},
                {"action": "Bribe the guards", "consequence": "They let you through for a price."},
            ]
        }
    )


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def clear_model_env(monkeypatch):
    monkeypatch.delenv("VENICE_MODEL", raising=False)


@pytest.mark.asyncio
async def test_invoke_returns_two_choices():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response(_well_formed_json()))
    )
    result = await client.invoke("You stand before the ruins.")
    assert len(result) == 2
    assert all(isinstance(c, Choice) for c in result)
    assert result[0].action == "Sneak past the guards"
    assert result[0].consequence == "You slip through undetected."
    assert result[1].action == "Bribe the guards"


@pytest.mark.asyncio
async def test_invoke_raises_on_malformed_response():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response("not valid json at all"))
    )
    with pytest.raises(OutputParserException):
        await client.invoke("You stand before the ruins.")


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
