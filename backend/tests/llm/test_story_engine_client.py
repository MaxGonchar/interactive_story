from __future__ import annotations

import types
from unittest.mock import AsyncMock

import pytest

from app.llm.story_engine_client import StoryEngineClient, _DEFAULT_MODEL
from app.models.domain import CharacterCard

DEFAULT_USER_CHARACTER = CharacterCard(id="c-1", name="Aria")
DEFAULT_SUPPORTING_CHARACTER = CharacterCard(id="c-2", name="Bram")


def _make_client() -> StoryEngineClient:
    return StoryEngineClient(
        user_character=DEFAULT_USER_CHARACTER,
        supporting_characters=[DEFAULT_SUPPORTING_CHARACTER],
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


@pytest.mark.asyncio
async def test_invoke_builds_expected_system_and_user_message_shape():
    client = _make_client()
    captured: list[list] = []

    async def _mock_ainvoke(messages):
        captured.append(messages)
        return _ai_response("ok")

    client._model = types.SimpleNamespace(ainvoke=_mock_ainvoke)
    await client.invoke(
        story_text="You approach the ruins.",
        action="Step inside",
        consequence="The darkness swallows you.",
    )

    system_prompt = captured[0][0].content
    user_prompt = captured[0][1].content

    assert "## Main Character Profile" in system_prompt
    assert "## Supporting Characters" in system_prompt

    main_section = system_prompt.split("## Main Character Profile", 1)[1].split(
        "## Supporting Characters", 1
    )[0]
    supporting_section = system_prompt.split("## Supporting Characters", 1)[1].split(
        "## Writing Style", 1
    )[0]

    assert "Aria" in main_section
    assert "Aria" not in supporting_section
    assert "Bram" in supporting_section

    assert "### Story" in user_prompt
    assert "### Action" in user_prompt
    assert "### Consequences" in user_prompt
    assert "You approach the ruins." in user_prompt
    assert "Step inside" in user_prompt
    assert "The darkness swallows you." in user_prompt


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
