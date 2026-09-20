from __future__ import annotations

import json
import types
from unittest.mock import AsyncMock

import pytest
from langchain_core.exceptions import OutputParserException

from app.llm.choice_engine_client import ChoiceEngineClient
from app.models.domain import CharacterCard, Choice

DEFAULT_USER_CHARACTER = CharacterCard(id="c-1", name="Aria")
DEFAULT_SUPPORTING_CHARACTER = CharacterCard(id="c-2", name="Bram")


def _make_client() -> ChoiceEngineClient:
    return ChoiceEngineClient(model=types.SimpleNamespace())


def _ai_response(content: str):
    return types.SimpleNamespace(
        content=content,
        response_metadata={
            "provider_model_id": "provider-choice",
            "provider_created": 1700000000,
            "cost_usd": 0.001,
            "duration_ms": 120,
        },
        usage_metadata={
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
        },
    )


def _well_formed_json() -> str:
    return json.dumps(
        {
            "options": [
                {"action": "Sneak past the guards", "consequence": "You slip through undetected."},
                {"action": "Bribe the guards", "consequence": "They let you through for a price."},
            ]
        }
    )


@pytest.mark.asyncio
async def test_invoke_returns_two_choices():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response(_well_formed_json()))
    )
    result = await client.invoke(
        "You stand before the ruins.",
        plot_direction="Head toward the ancient ruins.",
        user_character=DEFAULT_USER_CHARACTER,
        supporting_characters=[DEFAULT_SUPPORTING_CHARACTER],
    )
    assert len(result.result) == 2
    assert all(isinstance(c, Choice) for c in result.result)
    assert result.result[0].action == "Sneak past the guards"
    assert result.result[0].consequence == "You slip through undetected."
    assert result.result[1].action == "Bribe the guards"


@pytest.mark.asyncio
async def test_invoke_raises_on_malformed_response():
    client = _make_client()
    client._model = types.SimpleNamespace(
        ainvoke=AsyncMock(return_value=_ai_response("not valid json at all"))
    )
    with pytest.raises(OutputParserException):
        await client.invoke(
            "You stand before the ruins.",
            plot_direction="Head toward the ancient ruins.",
            user_character=DEFAULT_USER_CHARACTER,
            supporting_characters=[DEFAULT_SUPPORTING_CHARACTER],
        )


@pytest.mark.asyncio
async def test_invoke_prompt_contains_main_and_supporting_sections_without_leakage():
    client = _make_client()
    captured: list[list] = []

    async def _mock_ainvoke(messages):
        captured.append(messages)
        return _ai_response(_well_formed_json())

    client._model = types.SimpleNamespace(ainvoke=_mock_ainvoke)
    await client.invoke(
        "You stand before the ruins.",
        plot_direction="Head toward the ancient ruins.",
        user_character=DEFAULT_USER_CHARACTER,
        supporting_characters=[DEFAULT_SUPPORTING_CHARACTER],
    )

    system_prompt = captured[0][0].content
    assert "### Main Character Profile" in system_prompt
    assert "### Supporting Characters" in system_prompt

    main_section = system_prompt.split("### Main Character Profile", 1)[1].split(
        "### Supporting Characters", 1
    )[0]
    supporting_section = system_prompt.split("### Supporting Characters", 1)[1].split(
        "### Plot Development Direction", 1
    )[0]
    assert "Aria" in main_section
    assert "Aria" not in supporting_section
    assert "Bram" in supporting_section
