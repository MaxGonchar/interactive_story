from __future__ import annotations

from pydantic import BaseModel

from app.models.domain import CharacterCard, Message, SceneDescription


class VeniceUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class VeniceCost(BaseModel):
    usd: float


class VeniceCompletionMessage(BaseModel):
    content: str


class VeniceCompletionChoice(BaseModel):
    message: VeniceCompletionMessage


class VeniceCompletionResponse(BaseModel):
    model: str
    created: int
    choices: list[VeniceCompletionChoice]
    usage: VeniceUsage
    cost: VeniceCost | None = None


class VeniceCompletion(BaseModel):
    content: str
    provider_model_id: str
    created: int
    usage: VeniceUsage
    cost_usd: float | None = None
    duration_ms: int


class SceneContext(BaseModel):
    scene_description: SceneDescription
    characters: list[CharacterCard]
    user_character: CharacterCard | None
    messages: list[Message]
    context_data: list[str] = []
