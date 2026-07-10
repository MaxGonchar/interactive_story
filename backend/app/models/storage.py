from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from app.models.domain import StoryType


# ---------------------------------------------------------------------------
# Stories index  —  data/stories/index.yaml
# ---------------------------------------------------------------------------


class StoriesIndexEntry(BaseModel):
    id: str
    title: str
    created_at: str
    type: StoryType = "scene"


class StoriesIndex(BaseModel):
    stories: list[StoriesIndexEntry]


# ---------------------------------------------------------------------------
# Story metadata  —  data/stories/<story_id>/story.yaml
# ---------------------------------------------------------------------------


class StoryYaml(BaseModel):
    title: str
    scenes: list[int]


# ---------------------------------------------------------------------------
# Scene metadata  —  data/stories/<story_id>/scenes/<scene_id>/metadata.yaml
# ---------------------------------------------------------------------------


class SceneDescriptionYaml(BaseModel):
    general_scene_guide: str
    writing_style: str


class SceneMetadataYaml(BaseModel):
    finished: bool = False
    character_ids: list[str]
    user_character_id: str
    scene_description: SceneDescriptionYaml
    scene_summary: list[str] | None = None
    context: list[str] | None = None


# ---------------------------------------------------------------------------
# Character card  —  data/stories/<story_id>/characters/<character_id>.yaml
# ---------------------------------------------------------------------------


class CharacterYaml(BaseModel):
    name: str
    features: dict[str, str | list[str]] = {}
    memory: list[str] = []


# ---------------------------------------------------------------------------
# Scene messages  —  data/stories/<story_id>/scenes/<scene_id>/messages.yaml
# ---------------------------------------------------------------------------


class MessageYaml(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str


class MessagesYaml(BaseModel):
    messages: list[MessageYaml]


# ---------------------------------------------------------------------------
# Choice-driven story  —  data/stories/<story_id>/story.yaml (choice_driven)
# ---------------------------------------------------------------------------


class ChoiceDrivenStoryYaml(BaseModel):
    id: str
    title: str
    type: Literal["choice_driven"]
    character_ids: list[str]
    writing_style: str
    plot_directions: list[str]


# ---------------------------------------------------------------------------
# Choice-driven history  —  data/stories/<story_id>/history.yaml
# ---------------------------------------------------------------------------


class ChoiceYaml(BaseModel):
    action: str
    consequence: str


class StepYaml(BaseModel):
    id: int
    incoming_choice: ChoiceYaml | None
    text: str
    choices: list[ChoiceYaml]


class HistoryYaml(BaseModel):
    steps: list[StepYaml]
