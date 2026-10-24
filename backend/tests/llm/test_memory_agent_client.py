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

_NAMES = {"c1": "Mira", "c2": "Borin"}


def _message(id: int, author: str | None, action: str | None, narration: str):
    return CharacterDrivenMessage(
        id=id,
        input=None if action is None else CharacterDrivenInput(author=author, action=action),
        narration=narration,
        llm_data=CharacterDrivenLLMData(narrator_model_id="m", character_model_id=None),
    )


def _messages() -> list[CharacterDrivenMessage]:
    return [
        _message(1, None, None, "A storm rolls in."),
        _message(2, None, "I draw my sword.", "The hero draws a sword."),
        _message(3, "c1", "INTERNAL: afraid\nACTION: nods", "Mira nods."),
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
    result = build_scene_transcript(_messages(), _NAMES)

    assert result == (
        "A storm rolls in.\n\n"
        "Actor: Player\nI draw my sword.\n\nNarration:\nThe hero draws a sword.\n\n"
        "Actor: Mira\nINTERNAL: afraid\nACTION: nods\n\nNarration:\nMira nods."
    )


def test_transcript_renders_null_author_as_player():
    result = build_scene_transcript([_message(1, None, "Hello", "Hi.")], _NAMES)

    assert result.startswith("Actor: Player\n")


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
    assert "Wary and sharp" in system.content
    assert "- Lost her dagger" in system.content
    assert user.content.startswith("## Completed Scene\nA storm rolls in.")
    assert "Actor: Player" in user.content


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
