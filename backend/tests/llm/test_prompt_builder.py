from __future__ import annotations

from pathlib import Path

import pytest

from app.llm.models import SceneContext
from app.llm.prompt_builder import (
    CharacterDrivenPromptBuilder,
    PromptBuilder,
    build_character_agent_context,
)
from app.models.domain import (
    CharacterCard,
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    SceneDescription,
)


def _make_scene_description() -> SceneDescription:
    return SceneDescription(
        general_scene_guide="Focus on exploring the park together.",
        writing_style="Immersive, detail-oriented prose.",
    )


def _make_character(**kwargs) -> CharacterCard:
    defaults = dict(
        id="char-1",
        story_id="story-1",
        name="Sarah",
        features={},
        memory=[],
    )
    defaults.update(kwargs)
    return CharacterCard(**defaults)


def _make_user_character() -> CharacterCard:
    return CharacterCard(id="user-1", story_id="story-1", name="Mila")


def _story_message(
    message_id: int,
    author: str | None,
    narration: str,
    action: str | None = None,
    internal: str | None = None,
) -> CharacterDrivenMessage:
    return CharacterDrivenMessage(
        id=message_id,
        input=(
            None
            if action is None
            else CharacterDrivenInput(author=author, action=action, internal=internal)
        ),
        narration=narration,
        llm_data=CharacterDrivenLLMData(
            character_model_id=None, narrator_model_id="narrator"
        ),
    )


def _build(context: SceneContext) -> str:
    return PromptBuilder().build_system_prompt(context)


def test_character_driven_prompt_builder_loads_and_renders_template(tmp_path: Path):
    template_path = tmp_path / "character_system.j2"
    template_path.write_text("You are {{ character_name }}.", encoding="utf-8")

    result = CharacterDrivenPromptBuilder(tmp_path).render(
        "character_system.j2", character_name="Mira"
    )

    assert result == "You are Mira."


def test_character_agent_context_includes_only_owners_private_thoughts_in_order():
    messages = [
        _story_message(1, None, "Opening narration."),
        _story_message(
            2,
            "char-1",
            "Mira looks away.",
            action="Looks away.",
            internal="Mira's private thought.",
        ),
        _story_message(
            3,
            "char-2",
            "Borin raises a hand.",
            action="Raises a hand.",
            internal="Borin's private thought.",
        ),
        _story_message(
            4,
            "player",
            "The player answers.",
            action="I answer.",
            internal="The player's private thought.",
        ),
        _story_message(
            5,
            "char-1",
            "Mira approaches.",
            action=(
                "INTERNAL: Mira's legacy thought.\n\n"
                "ACTION: Mira approaches.\n\nSPEECH: Hello.\n\nTONE: Warm"
            ),
        ),
        _story_message(6, "char-2", "Borin nods.", action="Nods."),
    ]

    context = build_character_agent_context(
        _make_character(id="char-1"),
        messages,
        player_character_id="player",
    )

    assert context.current_scene_context == (
        "Opening narration.\n\n"
        "INTERNAL:\nMira's private thought.\n\nNarration:\nMira looks away.\n\n"
        "Borin raises a hand.\n\n"
        "The player answers.\n\n"
        "INTERNAL:\nMira's legacy thought.\n\nNarration:\nMira approaches.\n\n"
        "Borin nods."
    )


# --- acceptance criteria ---

def test_returns_non_empty_string():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        user_character=_make_user_character(),
        messages=[],
    )
    result = _build(ctx)
    assert isinstance(result, str)
    assert len(result) > 0


def test_does_not_contain_entry_point():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        user_character=_make_user_character(),
        messages=[],
    )
    assert "Scene Starting Point" not in _build(ctx)


def test_contains_context_data_items():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        user_character=_make_user_character(),
        messages=[],
        context_data=["It is raining.", "The door is locked."],
    )
    result = _build(ctx)
    assert "It is raining." in result
    assert "The door is locked." in result


def test_contains_character_names():
    chars = [
        _make_character(id="c1", name="Sarah"),
        _make_character(id="c2", name="Emma"),
    ]
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=chars,
        user_character=_make_user_character(),
        messages=[],
    )
    result = _build(ctx)
    assert "Sarah" in result
    assert "Emma" in result


def test_empty_characters_and_messages_does_not_raise():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        user_character=_make_user_character(),
        messages=[],
    )
    _build(ctx)  # must not raise


# --- edge cases ---

def test_character_with_all_optional_fields_none_does_not_raise():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[_make_character(name="Ghost")],
        user_character=_make_user_character(),
        messages=[],
    )
    result = _build(ctx)
    assert "Ghost" in result


def test_user_character_profile_in_prompt():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        user_character=_make_user_character(),
        messages=[],
    )
    result = _build(ctx)
    assert "Mila" in result


def test_narrator_prompt_omits_user_character_profile_and_uses_narrator_direction():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[_make_character(id="npc-1", name="Sarah")],
        user_character=None,
        messages=[],
    )

    result = _build(ctx)

    assert "User's Character Profile" not in result
    assert "The user directs the scene" in result
    assert "Sarah" in result
    assert "controlling the environment and all characters" in result


def test_hardcoded_protagonist_absent():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        user_character=_make_user_character(),
        messages=[],
    )
    result = _build(ctx)
    assert "Emma is a 18 years old girl" not in result


def test_character_with_all_optional_fields_populated():
    char = _make_character(
        name="Emma",
        features={
            "appearance": "Tall, red hair.",
            "traits": ["Brave", "Curious"],
            "speech_patterns": ["Short sentences."],
            "body_language": ["Crosses arms when nervous."],
            "likes": ["Coffee"],
            "fears": ["Heights"],
        },
        memory=["First meeting. Reflection: Felt at ease."],
    )
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[char],
        user_character=_make_user_character(),
        messages=[],
    )
    result = _build(ctx)
    assert "Tall, red hair." in result
    assert "Brave" in result
    assert "Coffee" in result
    assert "Heights" in result
    assert "First meeting." in result
