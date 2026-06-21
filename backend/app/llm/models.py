from pydantic import BaseModel

from app.models.domain import CharacterCard, Message, SceneDescription


class SceneContext(BaseModel):
    scene_description: SceneDescription
    characters: list[CharacterCard]
    user_character: CharacterCard
    messages: list[Message]
    context_data: list[str] = []
