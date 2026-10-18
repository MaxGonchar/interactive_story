from __future__ import annotations

import types
from unittest.mock import AsyncMock

import pytest

from app.exceptions import LLMError
from app.llm.character_agent_client import CharacterAgentClient
from app.models.domain import CharacterCard

_RAW = "INTERNAL: hmm\nACTION: nods\nSPEECH: \"Hi.\"\nTONE: calm\n"


def _character() -> CharacterCard:
    return CharacterCard(
        id="c1",
        name="Mira",
        features={"personality": "Wary and sharp", "goals": ["Find the key"]},
        memory=["Met the hero at the gate", "Lost her dagger"],
    )


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

    await client.invoke(_character(), ["First paragraph.", "Second paragraph."])

    system, user = captured[0]
    assert system.content.count("Wary and sharp") == 1
    assert system.content.count("Find the key") == 1
    assert "You are Mira." in system.content
    assert "CURRENT SCENE\nFirst paragraph.\n\nSecond paragraph." in user.content


@pytest.mark.asyncio
async def test_memories_rendered_only_via_dedicated_variable():
    client, captured = _client()

    await client.invoke(_character(), ["Scene."])

    system = captured[0][0].content
    assert system.count("Met the hero at the gate") == 1
    assert system.count("Lost her dagger") == 1
    assert "### Memory" not in system


@pytest.mark.asyncio
async def test_guidance_block_present_only_when_provided():
    client, captured = _client()

    await client.invoke(_character(), ["Scene."], player_guidance="Be bold")
    await client.invoke(_character(), ["Scene."])

    with_guidance, without_guidance = captured
    assert "## Player Guidance" in with_guidance[0].content
    assert "PLAYER GUIDANCE\nBe bold" in with_guidance[1].content
    assert "## Player Guidance" not in without_guidance[0].content
    assert "PLAYER GUIDANCE" not in without_guidance[1].content


# --- response handling ---

@pytest.mark.asyncio
async def test_raw_response_returned_unchanged():
    client, _ = _client()

    completion = await client.invoke(_character(), ["Scene."])

    assert completion.content == _RAW
    assert completion.result == _RAW


@pytest.mark.asyncio
@pytest.mark.parametrize("content", ["", "  \n "])
async def test_empty_response_raises_llm_error(content):
    client, _ = _client(content)

    with pytest.raises(LLMError):
        await client.invoke(_character(), ["Scene."])
