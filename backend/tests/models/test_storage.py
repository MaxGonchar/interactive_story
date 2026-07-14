from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.models.storage import (
    CharacterYaml,
    ChoiceDrivenStoryYaml,
    ChoiceYaml,
    HistoryYaml,
    MessageYaml,
    MessagesYaml,
    SceneDescriptionYaml,
    SceneMetadataYaml,
    StoriesIndex,
    StoriesIndexEntry,
    StepYaml,
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


def test_stories_index_entry_type_defaults_scene():
    entry = StoriesIndexEntry(
        id=STORY_ID,
        title="Mila and Bun",
        created_at="2024-06-01T12:00:00Z",
    )
    assert entry.type == "scene"


def test_stories_index_entry_type_choice_driven():
    entry = StoriesIndexEntry(
        id=STORY_ID,
        title="Mila and Bun",
        created_at="2024-06-01T12:00:00Z",
        type="choice_driven",
    )
    assert entry.type == "choice_driven"


def test_stories_index_parses_fixture_entry_type_defaults_scene():
    with open(f"{FIXTURE_ROOT}/index.yaml") as f:
        data = yaml.safe_load(f)
    index = StoriesIndex(**data)
    assert index.stories[0].type == "scene"


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
    assert story.title == "Mila and Bun"


def test_story_yaml_missing_title_raises():
    with pytest.raises(ValidationError):
        StoryYaml()


# ---------------------------------------------------------------------------
# SceneMetadataYaml / SceneDescriptionYaml
# ---------------------------------------------------------------------------


def test_scene_metadata_parses_fixture():
    with open(f"{FIXTURE_ROOT}/{STORY_ID}/scenes/1/meta.yaml") as f:
        data = yaml.safe_load(f)
    meta = SceneMetadataYaml(**data)
    assert meta.user_character_id == "max"
    assert isinstance(meta.scene_description, SceneDescriptionYaml)


def test_scene_metadata_scene_summary_is_optional_none():
    meta = SceneMetadataYaml(
        finished=False,
        character_ids=["mila"],
        user_character_id="max",
        scene_description=SceneDescriptionYaml(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
    )
    assert meta.scene_summary is None


def test_scene_metadata_yaml_context_defaults_none():
    meta = SceneMetadataYaml(
        finished=False,
        character_ids=["mila"],
        user_character_id="max",
        scene_description=SceneDescriptionYaml(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
    )
    assert meta.context is None


def test_scene_metadata_yaml_accepts_context_list():
    meta = SceneMetadataYaml(
        finished=False,
        character_ids=["mila"],
        user_character_id="max",
        scene_description=SceneDescriptionYaml(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
        context=["Context line one.", "Context line two."],
    )
    assert meta.context == ["Context line one.", "Context line two."]


def test_scene_metadata_accepts_scene_summary_list():
    meta = SceneMetadataYaml(
        finished=True,
        character_ids=["mila"],
        user_character_id="max",
        scene_description=SceneDescriptionYaml(
            general_scene_guide="G.",
            writing_style="S.",
        ),
        scene_summary=["A brief summary of the scene."],
    )
    assert meta.scene_summary == ["A brief summary of the scene."]


def test_scene_metadata_missing_character_ids_raises():
    with pytest.raises(ValidationError):
        SceneMetadataYaml(
            finished=False,
            user_character_id="max",
            scene_description=SceneDescriptionYaml(
                general_scene_guide="G.", writing_style="S."
            ),
        )


def test_scene_metadata_missing_user_character_id_raises():
    with pytest.raises(ValidationError):
        SceneMetadataYaml(
            finished=False,
            character_ids=["mila"],
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
    assert char.name == "Mila"


def test_character_yaml_defaults():
    char = CharacterYaml(name="Bun")
    assert char.features == {}
    assert char.memory == []


def test_character_yaml_with_features_and_memory():
    char = CharacterYaml(
        name="Bun",
        features={"appearance": "Fluffy.", "traits": ["Curious", "Playful"]},
        memory=["Learned to use a toilet."],
    )
    assert char.features["appearance"] == "Fluffy."
    assert char.features["traits"] == ["Curious", "Playful"]
    assert char.memory == ["Learned to use a toilet."]


def test_character_yaml_missing_name_raises():
    with pytest.raises(ValidationError):
        CharacterYaml()


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


# ---------------------------------------------------------------------------
# ChoiceDrivenStoryYaml
# ---------------------------------------------------------------------------


def test_choice_driven_story_yaml_fields():
    story = ChoiceDrivenStoryYaml(
        id="abc",
        title="Fog City",
        type="choice_driven",
        character_ids=["john"],
        writing_style="Dark and suspenseful",
        plot_directions=["Romance", "Betrayal"],
    )
    assert story.id == "abc"
    assert story.type == "choice_driven"
    assert story.plot_directions == ["Romance", "Betrayal"]


def test_choice_driven_story_yaml_missing_writing_style_raises():
    with pytest.raises(ValidationError):
        ChoiceDrivenStoryYaml(
            id="abc",
            title="Fog City",
            type="choice_driven",
            character_ids=[],
            plot_directions=[],
        )


# ---------------------------------------------------------------------------
# ChoiceYaml
# ---------------------------------------------------------------------------


def test_choice_yaml_fields():
    c = ChoiceYaml(action="Enter fog", consequence="A figure appears")
    assert c.action == "Enter fog"
    assert c.consequence == "A figure appears"


def test_choice_yaml_missing_field_raises():
    with pytest.raises(ValidationError):
        ChoiceYaml(action="only action")


# ---------------------------------------------------------------------------
# StepYaml
# ---------------------------------------------------------------------------


def test_step_yaml_first_step_no_incoming_choice():
    step = StepYaml(
        id=1,
        incoming_choice=None,
        text="The harbor fog rolled in.",
        choices=[ChoiceYaml(action="Enter", consequence="Mystery")],
    )
    assert step.incoming_choice is None
    assert len(step.choices) == 1


def test_step_yaml_with_incoming_choice():
    step = StepYaml(
        id=2,
        incoming_choice=ChoiceYaml(action="Run", consequence="Escape"),
        text="You flee.",
        choices=[],
    )
    assert step.incoming_choice.action == "Run"
    assert step.choices == []


def test_step_yaml_missing_text_raises():
    with pytest.raises(ValidationError):
        StepYaml(id=1, incoming_choice=None, choices=[])


# ---------------------------------------------------------------------------
# HistoryYaml
# ---------------------------------------------------------------------------


def test_history_yaml_empty_steps():
    h = HistoryYaml(steps=[])
    assert h.steps == []


def test_history_yaml_with_steps():
    h = HistoryYaml(
        steps=[
            StepYaml(id=1, incoming_choice=None, text="Intro.", choices=[]),
            StepYaml(
                id=2,
                incoming_choice=ChoiceYaml(action="Go", consequence="Arrive"),
                text="You arrive.",
                choices=[],
            ),
        ]
    )
    assert len(h.steps) == 2
    assert h.steps[0].id == 1


def test_history_yaml_missing_steps_raises():
    with pytest.raises(ValidationError):
        HistoryYaml()
