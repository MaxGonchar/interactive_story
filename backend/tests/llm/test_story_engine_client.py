from __future__ import annotations

import types
from unittest.mock import AsyncMock

import pytest

from app.llm.story_engine_client import StoryEngineClient
from app.models.domain import CharacterCard

DEFAULT_USER_CHARACTER = CharacterCard(id="c-1", name="Aria")
DEFAULT_SUPPORTING_CHARACTER = CharacterCard(id="c-2", name="Bram")


def _make_client() -> StoryEngineClient:
    return StoryEngineClient(model=types.SimpleNamespace())


def _ai_response(content: str):
    return types.SimpleNamespace(content=content)


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
        user_character=DEFAULT_USER_CHARACTER,
        supporting_characters=[DEFAULT_SUPPORTING_CHARACTER],
        writing_style="Dark and atmospheric.",
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
        user_character=DEFAULT_USER_CHARACTER,
        supporting_characters=[DEFAULT_SUPPORTING_CHARACTER],
        writing_style="Dark and atmospheric.",
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
