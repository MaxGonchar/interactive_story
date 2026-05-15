from pydantic import BaseModel

from app.models.domain import CharacterCard, Message, SceneDescription


class SceneContext(BaseModel):
    scene_description: SceneDescription
    characters: list[CharacterCard]
    messages: list[Message]
