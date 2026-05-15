import pytest

from app.llm.models import SceneContext
from app.llm.prompt_builder import PromptBuilder
from app.models.domain import CharacterCard, MemoryEntry, SceneDescription


def _make_scene_description() -> SceneDescription:
    return SceneDescription(
        entry_point="The path leads into the old park.",
        general_scene_guide="Focus on exploring the park together.",
        writing_style="Immersive, detail-oriented prose.",
    )


def _make_character(**kwargs) -> CharacterCard:
    defaults = dict(
        id="char-1",
        story_id="story-1",
        name="Sarah",
        appearance=None,
        traits=None,
        speech_patterns=None,
        body_language=None,
        likes=None,
        fears=None,
        memory=None,
    )
    defaults.update(kwargs)
    return CharacterCard(**defaults)


def _build(context: SceneContext) -> str:
    return PromptBuilder().build_system_prompt(context)


# --- acceptance criteria ---

def test_returns_non_empty_string():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        messages=[],
    )
    result = _build(ctx)
    assert isinstance(result, str)
    assert len(result) > 0


def test_contains_entry_point():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        messages=[],
    )
    assert "The path leads into the old park." in _build(ctx)


def test_contains_context_data_items():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
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
        messages=[],
    )
    result = _build(ctx)
    assert "Sarah" in result
    assert "Emma" in result


def test_empty_characters_and_messages_does_not_raise():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[],
        messages=[],
    )
    _build(ctx)  # must not raise


# --- edge cases ---

def test_character_with_all_optional_fields_none_does_not_raise():
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[_make_character(name="Ghost")],
        messages=[],
    )
    result = _build(ctx)
    assert "Ghost" in result


def test_character_with_all_optional_fields_populated():
    char = _make_character(
        name="Emma",
        appearance="Tall, red hair.",
        traits=["Brave", "Curious"],
        speech_patterns=["Short sentences."],
        body_language=["Crosses arms when nervous."],
        likes=["Coffee"],
        fears=["Heights"],
        memory=[MemoryEntry(case="First meeting", reflection="Felt at ease.")],
    )
    ctx = SceneContext(
        scene_description=_make_scene_description(),
        characters=[char],
        messages=[],
    )
    result = _build(ctx)
    assert "Tall, red hair." in result
    assert "Brave" in result
    assert "Coffee" in result
    assert "Heights" in result
    assert "First meeting" in result

