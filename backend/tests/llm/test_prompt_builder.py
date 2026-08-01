from __future__ import annotations

import pytest

from app.llm.models import SceneContext
from app.llm.prompt_builder import PromptBuilder
from app.models.domain import CharacterCard, SceneDescription


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


def _build(context: SceneContext) -> str:
    return PromptBuilder().build_system_prompt(context)


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

