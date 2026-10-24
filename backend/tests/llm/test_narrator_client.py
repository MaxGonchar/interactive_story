from __future__ import annotations

import types

import pytest

from app.exceptions import LLMError
from app.llm.narrator_client import NarratorClient
from app.llm.prompt_builder import build_narrator_context

_TURN = 'INTERNAL: hmm\nACTION: nods\nSPEECH: "Hi."\nTONE: calm'


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


def _client(content="The door creaks open."):
    captured: list[list] = []

    async def _ainvoke(messages):
        captured.append(messages)
        return _ai_response(content)

    return NarratorClient(model=types.SimpleNamespace(ainvoke=_ainvoke)), captured


async def _invoke(client, turn=_TURN):
    return await client.invoke(
        story_context=["Fact one", "Fact two"],
        general_scene_guide="Tense standoff",
        writing_style="Noir",
        scene_narrations=["Opening.", "Second."],
        actor_name="Mira",
        current_turn=turn,
    )


# --- builder ---

def test_builder_context_fields():
    context = build_narrator_context(
        ["Fact one", "Fact two"], "Guide", "Style", ["Opening.", "Second."], "Mira", "Acts"
    )

    assert context.model_dump() == {
        "story_context": "* Fact one\n* Fact two",
        "general_scene_guide": "Guide",
        "writing_style": "Style",
        "current_scene_context": "Opening.\n\nSecond.",
        "actor_name": "Mira",
        "current_turn": "Acts",
    }


# --- prompt rendering ---

@pytest.mark.asyncio
async def test_user_message_has_history_then_actor_then_turn():
    client, captured = _client()

    await _invoke(client)

    assert captured[0][1].content == (
        "SCENE SO FAR\nOpening.\n\nSecond.\n\n"
        f"TURN TO NARRATE (not yet in the scene)\nActor: Mira\n{_TURN}\n\n"
        "Write the next paragraph so it narrates this turn first.\n"
    )


@pytest.mark.asyncio
async def test_system_prompt_contains_configuration():
    client, captured = _client()

    await _invoke(client)

    system = captured[0][0].content
    assert "* Fact one\n* Fact two" in system
    assert "## General Direction of Development\nTense standoff" in system
    assert "## Style of Telling\nNoir" in system


@pytest.mark.asyncio
async def test_system_prompt_requires_narrating_the_turn():
    client, captured = _client()

    await _invoke(client)

    system = captured[0][0].content
    assert "MUST begin by narrating the current turn" in system
    assert "The current turn is not history" in system
    assert "never output the field labels" in system


# --- response handling ---

@pytest.mark.asyncio
async def test_returns_narrator_text():
    client, _ = _client("The door creaks open.")

    completion = await _invoke(client)

    assert completion.result == "The door creaks open."


@pytest.mark.asyncio
@pytest.mark.parametrize("content", ["", "  \n "])
async def test_empty_response_raises_llm_error(content):
    client, _ = _client(content)

    with pytest.raises(LLMError):
        await _invoke(client)
