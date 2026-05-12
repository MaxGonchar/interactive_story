from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Stories index  —  data/stories/index.yaml
# ---------------------------------------------------------------------------


class StoriesIndexEntry(BaseModel):
    id: str
    title: str
    created_at: str


class StoriesIndex(BaseModel):
    stories: list[StoriesIndexEntry]


# ---------------------------------------------------------------------------
# Story metadata  —  data/stories/<story_id>/story.yaml
# ---------------------------------------------------------------------------


class SceneRefYaml(BaseModel):
    id: int
    finished: bool
    summary: list[str] | None = None


class StoryYaml(BaseModel):
    id: str
    title: str
    character_ids: list[str]
    scenes: list[SceneRefYaml]


# ---------------------------------------------------------------------------
# Scene metadata  —  data/stories/<story_id>/scenes/<scene_id>/metadata.yaml
# ---------------------------------------------------------------------------


class SceneDescriptionYaml(BaseModel):
    entry_point: str
    general_scene_guide: str
    writing_style: str


class SceneMetadataYaml(BaseModel):
    id: int
    story_id: str | None = None
    finished: bool = False
    characters_ids: list[str]
    scene_description: SceneDescriptionYaml
    scene_summary: str | None = None


# ---------------------------------------------------------------------------
# Character card  —  data/stories/<story_id>/characters/<character_id>.yaml
# ---------------------------------------------------------------------------


class CharacterMemoryEntryYaml(BaseModel):
    case: str
    reflection: str


class CharacterYaml(BaseModel):
    id: str
    story_id: str | None = None
    name: str
    appearance: str | None = None
    traits: list[str] | None = None
    speech_patterns: list[str] | None = None
    body_language: list[str] | None = None
    likes: list[str] | None = None
    fears: list[str] | None = None
    memory: list[CharacterMemoryEntryYaml] | None = None


# ---------------------------------------------------------------------------
# Scene messages  —  data/stories/<story_id>/scenes/<scene_id>/messages.yaml
# ---------------------------------------------------------------------------


class MessageYaml(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str


class MessagesYaml(BaseModel):
    messages: list[MessageYaml]
