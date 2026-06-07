import pytest
from pydantic import ValidationError

from app.models.domain import (
    CharacterCard,
    MemoryEntry,
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
        character_ids=["mila", "bun"],
        scenes=[SceneRef(id=1, finished=True), SceneRef(id=2, finished=False)],
        active_scene_id=2,
    )
    assert meta.active_scene_id == 2
    assert len(meta.scenes) == 2


def test_story_meta_active_scene_id_none():
    meta = StoryMeta(
        id="abc",
        title="Test",
        character_ids=[],
        scenes=[],
        active_scene_id=None,
    )
    assert meta.active_scene_id is None


def test_memory_entry():
    entry = MemoryEntry(case="A case description.", reflection="A reflection.")
    assert entry.case == "A case description."


def test_character_card_full():
    card = CharacterCard(
        id="mila",
        story_id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        name="Mila",
        appearance="Tall and wiry.",
        traits=["Cynical", "Resourceful"],
        speech_patterns=["Uses gardening metaphors."],
        body_language=["Rarely stands still."],
        likes=["Rain on dry earth."],
        fears=["Sterile corporate spaces."],
        memory=[MemoryEntry(case="Day one.", reflection="Reflection one.")],
    )
    assert card.story_id == "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
    assert card.traits == ["Cynical", "Resourceful"]


def test_character_card_optional_fields_default_none():
    card = CharacterCard(id="bun", story_id="abc", name="Bun")
    assert card.appearance is None
    assert card.traits is None
    assert card.memory is None


def test_character_card_optional_fields_accept_empty_lists():
    card = CharacterCard(
        id="bun",
        story_id="abc",
        name="Bun",
        traits=[],
        speech_patterns=[],
        body_language=[],
        likes=[],
        fears=[],
        memory=[],
    )
    assert card.traits == []
    assert card.memory == []


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
