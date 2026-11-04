from __future__ import annotations

import types
from unittest.mock import AsyncMock

import pytest

from app.exceptions import LLMError
from app.llm.character_agent_client import CharacterAgentClient
from app.models.domain import (
    CharacterCard,
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    CharacterTurnOutput,
)

_RAW = (
    '{"internal":"hmm","action":"nods","speech":"\\"Hi.\\"",'
    '"tone":"calm"}'
)
_OUTPUT = CharacterTurnOutput(
    internal="hmm", action="nods", speech='"Hi."', tone="calm"
)


def _character() -> CharacterCard:
    return CharacterCard(
        id="c1",
        name="Mira",
        features={"personality": "Wary and sharp", "goals": ["Find the key"]},
        memory=["Met the hero at the gate", "Lost her dagger"],
    )


def _scene_messages(*narrations: str) -> list[CharacterDrivenMessage]:
    return [
        CharacterDrivenMessage(
            id=index,
            input=None,
            narration=narration,
            llm_data=CharacterDrivenLLMData(
                character_model_id=None, narrator_model_id="narrator"
            ),
        )
        for index, narration in enumerate(narrations, start=1)
    ]


def _ai_response(content):
    return types.SimpleNamespace(
        content=content,
        response_metadata={
            "provider_model_id": "provider-model",
            "provider_created": 1700000000,
            "cost_usd": 0.001,
            "duration_ms": 120,
        },
        usage_metadata={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    )


def _client(content=_RAW):
    captured: list[list] = []

    async def _ainvoke(messages):
        captured.append(messages)
        return _ai_response(content)

    return CharacterAgentClient(model=types.SimpleNamespace(ainvoke=_ainvoke)), captured


# --- prompt rendering ---

@pytest.mark.asyncio
async def test_prompt_contains_profile_once_and_scene_narration():
    client, captured = _client()

    await client.invoke(_character(), _scene_messages("First paragraph.", "Second paragraph."))

    system, user = captured[0]
    assert system.content.count("Wary and sharp") == 1
    assert system.content.count("Find the key") == 1
    assert "You are Mira." in system.content
    assert "CURRENT SCENE\nFirst paragraph.\n\nSecond paragraph." in user.content


@pytest.mark.asyncio
async def test_memories_rendered_only_via_dedicated_variable():
    client, captured = _client()

    await client.invoke(_character(), _scene_messages("Scene."))

    system = captured[0][0].content
    assert system.count("Met the hero at the gate") == 1
    assert system.count("Lost her dagger") == 1
    assert "### Memory" not in system


@pytest.mark.asyncio
async def test_guidance_block_present_only_when_provided():
    client, captured = _client()

    await client.invoke(_character(), _scene_messages("Scene."), player_guidance="Be bold")
    await client.invoke(_character(), _scene_messages("Scene."))

    with_guidance, without_guidance = captured
    assert "## Player Guidance" in with_guidance[0].content
    assert "PLAYER GUIDANCE\nBe bold" in with_guidance[1].content
    assert "## Player Guidance" not in without_guidance[0].content
    assert "PLAYER GUIDANCE" not in without_guidance[1].content


# TODO: test particular text instead of testing that some parts are in the text.
@pytest.mark.asyncio
async def test_context_contains_only_owners_private_thoughts():
    client, captured = _client()
    messages = [
        CharacterDrivenMessage(
            id=1,
            input=CharacterDrivenInput(
                author="c1", action="She nods.", internal="Mira's private thought."
            ),
            narration="Mira nods.",
            llm_data={"character_model_id": "m", "narrator_model_id": "n"},
        ),
        CharacterDrivenMessage(
            id=2,
            input=CharacterDrivenInput(
                author="c2", action="He waves.", internal="Borin's private thought."
            ),
            narration="Borin waves.",
            llm_data={"character_model_id": "m", "narrator_model_id": "n"},
        ),
        CharacterDrivenMessage(
            id=3,
            input=CharacterDrivenInput(
                author="player",
                action="The player replies.",
                internal="The player's private thought.",
            ),
            narration="The player replies.",
            llm_data={"character_model_id": None, "narrator_model_id": "n"},
        ),
    ]

    await client.invoke(_character(), messages, player_character_id="player")

    current_scene = captured[0][1].content
    assert "INTERNAL:\nMira's private thought.\n\nNarration:\nMira nods." in current_scene
    assert "Borin's private thought." not in current_scene
    assert "The player's private thought." not in current_scene
    assert "Borin waves." in current_scene
    assert "The player replies." in current_scene


# --- response handling ---

@pytest.mark.asyncio
async def test_structured_response_is_parsed():
    client, _ = _client()

    completion = await client.invoke(_character(), _scene_messages("Scene."))

    assert completion.content == _RAW
    assert completion.result == _OUTPUT
    assert completion.result.action == "nods"


@pytest.mark.asyncio
@pytest.mark.parametrize("content", ["", "  \n "])
async def test_empty_response_raises_llm_error(content):
    client, _ = _client(content)

    with pytest.raises(LLMError):
        await client.invoke(_character(), _scene_messages("Scene."))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content",
    [
        "INTERNAL: hmm\nACTION: nods\nSPEECH: Hi.\nTONE: calm",
        '{"internal":"hmm","action":"nods"}',
    ],
)
async def test_invalid_structured_response_raises_llm_error(content):
    client, _ = _client(content)

    with pytest.raises(LLMError, match="invalid structured output"):
        await client.invoke(_character(), _scene_messages("Scene."))


@pytest.mark.asyncio
async def test_prompt_requests_structured_output_with_all_fields():
    client, captured = _client()

    await client.invoke(_character(), _scene_messages("Scene."))

    system_prompt = captured[0][0].content
    assert '"internal":' in system_prompt
    assert '"action":' in system_prompt
    assert '"speech":' in system_prompt
    assert '"tone":' in system_prompt
