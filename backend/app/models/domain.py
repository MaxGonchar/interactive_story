from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class StoryIndexItem(BaseModel):
    id: str
    title: str
    created_at: str


class SceneRef(BaseModel):
    id: int
    finished: bool
    summary: list[str] | None = None


class StoryMeta(BaseModel):
    id: str
    title: str
    character_ids: list[str]
    scenes: list[SceneRef]
    active_scene_id: int | None


class MemoryEntry(BaseModel):
    case: str
    reflection: str


class CharacterCard(BaseModel):
    id: str
    story_id: str
    name: str
    appearance: str | None = None
    traits: list[str] | None = None
    speech_patterns: list[str] | None = None
    body_language: list[str] | None = None
    likes: list[str] | None = None
    fears: list[str] | None = None
    memory: list[MemoryEntry] | None = None


class SceneDescription(BaseModel):
    general_scene_guide: str
    writing_style: str


class SceneMetadata(BaseModel):
    id: int
    story_id: str
    characters_ids: list[str]
    finished: bool
    scene_description: SceneDescription
    scene_summary: list[str] | None = None


class Message(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str
