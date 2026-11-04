from __future__ import annotations

import json
import types
from unittest.mock import AsyncMock

import pytest

from app.exceptions import LLMError
from app.llm.memory_agent_client import MemoryAgentClient
from app.llm.prompt_builder import build_scene_transcript
from app.models.domain import (
    CharacterCard,
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
)

_NAMES = {"c1": "Mira", "c2": "Borin", "player": "The Player"}


def _message(
    id: int,
    author: str | None,
    action: str | None,
    narration: str,
    internal: str | None = None,
):
    return CharacterDrivenMessage(
        id=id,
        input=(
            None
            if action is None
            else CharacterDrivenInput(author=author, action=action, internal=internal)
        ),
        narration=narration,
        llm_data=CharacterDrivenLLMData(narrator_model_id="m", character_model_id=None),
    )


def _messages() -> list[CharacterDrivenMessage]:
    return [
        _message(1, None, None, "A storm rolls in."),
        _message(2, None, "I draw my sword.", "The hero draws a sword."),
        _message(
            3,
            "c1",
            "INTERNAL: afraid\n\nACTION: nods",
            "Mira nods.",
        ),
        _message(
            4,
            "c2",
            "Borin raises a lantern.",
            "Borin raises a lantern.",
            internal="Borin's private thought.",
        ),
        _message(
            5,
            "player",
            "The player waits.",
            "The player waits.",
            internal="The player's private thought.",
        ),
    ]


def _character() -> CharacterCard:
    return CharacterCard(
        id="c1",
        name="Mira",
        features={"personality": "Wary and sharp"},
        memory=["Lost her dagger"],
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


def _client(content):
    captured: list[list] = []

    async def _ainvoke(messages):
        captured.append(messages)
        return _ai_response(content)

    return MemoryAgentClient(model=types.SimpleNamespace(ainvoke=_ainvoke)), captured


# --- transcript ---

def test_transcript_lists_entries_in_order_with_actor_action_and_narration():
    result = build_scene_transcript(
        _messages(), _NAMES, "c1", player_character_id="player"
    )

    assert result == (
        "A storm rolls in.\n\n"
        "Actor: Player\nI draw my sword.\n\nNarration:\nThe hero draws a sword.\n\n"
        "Actor: Mira\nACTION: nods\n\nINTERNAL:\nafraid\n\nNarration:\nMira nods.\n\n"
        "Actor: Borin\nBorin raises a lantern.\n\nNarration:\nBorin raises a lantern.\n\n"
        "Actor: The Player\nThe player waits.\n\nNarration:\nThe player waits."
    )


def test_transcript_renders_null_author_as_player():
    result = build_scene_transcript(
        [_message(1, None, "Hello", "Hi.")], _NAMES, "c1"
    )

    assert result.startswith("Actor: Player\n")


def test_transcript_includes_only_memory_owners_internal_thoughts():
    result = build_scene_transcript(
        _messages(), _NAMES, "c2", player_character_id="player"
    )

    assert "Borin's private thought." in result
    assert "afraid" not in result
    assert "The player's private thought." not in result
    assert "A storm rolls in." in result
    assert "Borin raises a lantern." in result


# --- invoke ---

@pytest.mark.asyncio
async def test_invoke_returns_list_of_strings():
    client, _ = _client(json.dumps({"items": ["Mira met the hero."]}))

    result = await client.invoke(_character(), _messages(), _NAMES)

    assert result.result == ["Mira met the hero."]


@pytest.mark.asyncio
async def test_prompt_contains_character_memories_and_transcript():
    client, captured = _client(json.dumps({"items": []}))

    await client.invoke(_character(), _messages(), _NAMES)

    system, user = captured[0]
    assert "propose new memories for Mira" in system.content
    assert "INTERNAL blocks are private thoughts belonging only to Mira" in system.content
    assert "Wary and sharp" in system.content
    assert "- Lost her dagger" in system.content
    assert user.content.startswith("## Completed Scene\nA storm rolls in.")
    assert "Actor: Player" in user.content
    assert "afraid" in user.content
    assert "Borin's private thought." not in user.content
    assert "The player's private thought." not in user.content


@pytest.mark.asyncio
async def test_prompt_without_memories_shows_placeholder():
    client, captured = _client(json.dumps({"items": []}))
    character = _character().model_copy(update={"memory": []})

    await client.invoke(character, _messages(), _NAMES)

    assert "(No existing memories.)" in captured[0][0].content


@pytest.mark.asyncio
async def test_invoke_raises_on_malformed_response():
    client, _ = _client("not valid json at all")

    with pytest.raises(LLMError, match="invalid structured output"):
        await client.invoke(_character(), _messages(), _NAMES)


@pytest.mark.asyncio
async def test_invoke_raises_on_non_text_response_content():
    client, _ = _client([{"type": "text", "text": "hello"}])

    with pytest.raises(TypeError, match="non-text"):
        await client.invoke(_character(), _messages(), _NAMES)


@pytest.mark.asyncio
async def test_llm_error_propagates():
    client = MemoryAgentClient(
        model=types.SimpleNamespace(ainvoke=AsyncMock(side_effect=RuntimeError("down")))
    )

    with pytest.raises(RuntimeError, match="down"):
        await client.invoke(_character(), _messages(), _NAMES)
