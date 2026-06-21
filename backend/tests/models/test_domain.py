import pytest
from pydantic import ValidationError

from app.models.domain import (
    CharacterCard,
    Message,
    SceneDescription,
    SceneMetadata,
    SceneRef,
    StoryIndexItem,
    StoryMeta,
)


def test_story_index_item():
    item = StoryIndexItem(
        id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        title="Mila and Bun",
        created_at="2024-06-01T12:00:00Z",
    )
    assert item.id == "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
    assert item.title == "Mila and Bun"


def test_scene_ref_with_summary():
    ref = SceneRef(id=1, finished=True, summary=["Scene one summary."])
    assert ref.finished is True
    assert ref.summary == ["Scene one summary."]


def test_scene_ref_summary_defaults_none():
    ref = SceneRef(id=2, finished=False)
    assert ref.summary is None


def test_story_meta():
    meta = StoryMeta(
        id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        title="Mila and Bun",
        user_character_id="max",
        character_ids=["mila", "bun"],
        scenes=[SceneRef(id=1, finished=True), SceneRef(id=2, finished=False)],
        active_scene_id=2,
    )
    assert meta.active_scene_id == 2
    assert meta.user_character_id == "max"
    assert len(meta.scenes) == 2


def test_story_meta_active_scene_id_none():
    meta = StoryMeta(
        id="abc",
        title="Test",
        user_character_id="max",
        character_ids=[],
        scenes=[],
        active_scene_id=None,
    )
    assert meta.active_scene_id is None


def test_character_card_defaults():
    card = CharacterCard(id="bun", story_id="abc", name="Bun")
    assert card.features == {}
    assert card.memory == []


def test_character_card_with_features_and_memory():
    card = CharacterCard(
        id="mila",
        story_id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        name="Mila",
        features={
            "appearance": "Tall and wiry.",
            "traits": ["Cynical", "Resourceful"],
        },
        memory=["Day one. Reflection: Felt overwhelmed."],
    )
    assert card.features["traits"] == ["Cynical", "Resourceful"]
    assert card.memory == ["Day one. Reflection: Felt overwhelmed."]


# ---------------------------------------------------------------------------
# CharacterCard.to_prompt_text()
# ---------------------------------------------------------------------------


def test_to_prompt_text_string_feature_renders_as_plain_text():
    card = CharacterCard(
        id="c", story_id="s", name="Ghost",
        features={"appearance": "Tall and pale."},
    )
    result = card.to_prompt_text()
    assert "### Appearance" in result
    assert "Tall and pale." in result


def test_to_prompt_text_list_feature_renders_as_bullet_points():
    card = CharacterCard(
        id="c", story_id="s", name="Ghost",
        features={"traits": ["Brave", "Curious"]},
    )
    result = card.to_prompt_text()
    assert "### Traits" in result
    assert "- Brave" in result
    assert "- Curious" in result


def test_to_prompt_text_feature_key_is_title_cased():
    card = CharacterCard(
        id="c", story_id="s", name="Ghost",
        features={"speech_patterns": ["Short sentences."]},
    )
    result = card.to_prompt_text()
    assert "### Speech Patterns" in result


def test_to_prompt_text_memory_section_present_when_non_empty():
    card = CharacterCard(
        id="c", story_id="s", name="Ghost",
        memory=["Encountered a stranger."],
    )
    result = card.to_prompt_text()
    assert "### Memory" in result
    assert "- Encountered a stranger." in result


def test_to_prompt_text_memory_section_omitted_when_empty():
    card = CharacterCard(id="c", story_id="s", name="Ghost", memory=[])
    result = card.to_prompt_text()
    assert "### Memory" not in result


def test_to_prompt_text_empty_features_produces_only_name_header():
    card = CharacterCard(id="c", story_id="s", name="Ghost")
    result = card.to_prompt_text()
    assert result == "## Ghost"


def test_scene_description():
    desc = SceneDescription(
        general_scene_guide="Guide text.",
        writing_style="Stark and physical.",
    )
    assert desc.general_scene_guide == "Guide text."


def test_scene_metadata():
    meta = SceneMetadata(
        id=1,
        story_id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        characters_ids=["mila", "bun"],
        finished=False,
        scene_description=SceneDescription(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
    )
    assert meta.scene_summary is None
    assert meta.characters_ids == ["mila", "bun"]


def test_scene_metadata_with_summary():
    meta = SceneMetadata(
        id=1,
        story_id="abc",
        characters_ids=["mila"],
        finished=True,
        scene_description=SceneDescription(
            general_scene_guide="G.", writing_style="S."
        ),
        scene_summary=["Summary line one.", "Summary line two."],
    )
    assert meta.scene_summary == ["Summary line one.", "Summary line two."]


def test_message_valid():
    msg = Message(id=1, role="assistant", content="Hello.")
    assert msg.role == "assistant"


def test_message_user_role():
    msg = Message(id=2, role="user", content="Hi.")
    assert msg.role == "user"


def test_message_invalid_role_raises():
    with pytest.raises(ValidationError):
        Message(id=3, role="narrator", content="Narration.")
