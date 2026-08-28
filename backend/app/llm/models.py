from __future__ import annotations

from pydantic import BaseModel

from app.models.domain import CharacterCard, Message, SceneDescription


class SceneContext(BaseModel):
    scene_description: SceneDescription
    characters: list[CharacterCard]
    user_character: CharacterCard | None
    messages: list[Message]
    context_data: list[str] = []
