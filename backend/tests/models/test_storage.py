from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.models.storage import (
    CharacterMemoryEntryYaml,
    CharacterYaml,
    MessageYaml,
    MessagesYaml,
    SceneDescriptionYaml,
    SceneMetadataYaml,
    SceneRefYaml,
    StoriesIndex,
    StoriesIndexEntry,
    StoryYaml,
)

STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
FIXTURE_ROOT = Path(__file__).parents[3] / "data-test" / "stories"


# ---------------------------------------------------------------------------
# StoriesIndex
# ---------------------------------------------------------------------------


def test_stories_index_parses_fixture():
    with open(f"{FIXTURE_ROOT}/index.yaml") as f:
        data = yaml.safe_load(f)
    index = StoriesIndex(**data)
    assert len(index.stories) >= 1
    assert isinstance(index.stories[0], StoriesIndexEntry)


def test_stories_index_entry_fields():
    entry = StoriesIndexEntry(
        id=STORY_ID,
        title="Mila and Bun",
        created_at="2024-06-01T12:00:00Z",
    )
    assert entry.id == STORY_ID
    assert entry.title == "Mila and Bun"


def test_stories_index_missing_stories_raises():
    with pytest.raises(ValidationError):
        StoriesIndex()


# ---------------------------------------------------------------------------
# StoryYaml / SceneRefYaml
# ---------------------------------------------------------------------------


def test_story_yaml_parses_fixture():
    with open(f"{FIXTURE_ROOT}/{STORY_ID}/story.yaml") as f:
        data = yaml.safe_load(f)
    story = StoryYaml(**data)
    assert story.id == STORY_ID
    assert len(story.scenes) >= 1
    assert isinstance(story.scenes[0], SceneRefYaml)


def test_scene_ref_yaml_with_summary():
    ref = SceneRefYaml(id=1, finished=True, summary=["Line one.", "Line two."])
    assert ref.finished is True
    assert ref.summary == ["Line one.", "Line two."]


def test_scene_ref_yaml_summary_defaults_none():
    ref = SceneRefYaml(id=2, finished=False)
    assert ref.summary is None


def test_story_yaml_missing_id_raises():
    with pytest.raises(ValidationError):
        StoryYaml(title="X", character_ids=[], scenes=[])


# ---------------------------------------------------------------------------
# SceneMetadataYaml / SceneDescriptionYaml
# ---------------------------------------------------------------------------


def test_scene_metadata_parses_fixture():
    with open(f"{FIXTURE_ROOT}/{STORY_ID}/scenes/1/meta.yaml") as f:
        data = yaml.safe_load(f)
    meta = SceneMetadataYaml(**data)
    assert meta.id == 1
    assert isinstance(meta.scene_description, SceneDescriptionYaml)


def test_scene_metadata_scene_summary_is_optional_none():
    meta = SceneMetadataYaml(
        id=1,
        finished=False,
        characters_ids=["mila"],
        scene_description=SceneDescriptionYaml(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
    )
    assert meta.scene_summary is None


def test_scene_metadata_accepts_scene_summary_list():
    meta = SceneMetadataYaml(
        id=1,
        finished=True,
        characters_ids=["mila"],
        scene_description=SceneDescriptionYaml(
            general_scene_guide="G.",
            writing_style="S.",
        ),
        scene_summary=["A brief summary of the scene."],
    )
    assert meta.scene_summary == ["A brief summary of the scene."]


def test_scene_metadata_missing_characters_ids_raises():
    with pytest.raises(ValidationError):
        SceneMetadataYaml(
            id=1,
            finished=False,
            scene_description=SceneDescriptionYaml(
                general_scene_guide="G.", writing_style="S."
            ),
        )


# ---------------------------------------------------------------------------
# CharacterYaml
# ---------------------------------------------------------------------------


def test_character_yaml_parses_fixture():
    with open(f"{FIXTURE_ROOT}/{STORY_ID}/characters/mila.yaml") as f:
        data = yaml.safe_load(f)
    char = CharacterYaml(**data)
    assert char.id == "mila"
    assert char.name == "Mila"


def test_character_yaml_optional_fields_default_none():
    char = CharacterYaml(id="bun", name="Bun")
    assert char.appearance is None
    assert char.traits is None
    assert char.memory is None
    assert char.story_id is None


def test_character_memory_entry_yaml():
    entry = CharacterMemoryEntryYaml(case="A case.", reflection="A reflection.")
    assert entry.case == "A case."


def test_character_yaml_missing_name_raises():
    with pytest.raises(ValidationError):
        CharacterYaml(id="bun")


# ---------------------------------------------------------------------------
# MessagesYaml / MessageYaml
# ---------------------------------------------------------------------------


def test_messages_yaml_parses_fixture():
    with open(f"{FIXTURE_ROOT}/{STORY_ID}/scenes/1/messages.yaml") as f:
        data = yaml.safe_load(f)
    msgs = MessagesYaml(**data)
    assert len(msgs.messages) >= 1
    assert isinstance(msgs.messages[0], MessageYaml)


def test_message_yaml_valid_roles():
    user_msg = MessageYaml(id=1, role="user", content="Hello.")
    asst_msg = MessageYaml(id=2, role="assistant", content="Hi.")
    assert user_msg.role == "user"
    assert asst_msg.role == "assistant"


def test_message_yaml_invalid_role_raises():
    with pytest.raises(ValidationError):
        MessageYaml(id=3, role="narrator", content="Narration.")


def test_messages_yaml_missing_messages_raises():
    with pytest.raises(ValidationError):
        MessagesYaml()
