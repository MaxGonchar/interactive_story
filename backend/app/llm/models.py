from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.models.domain import CharacterCard, Message, SceneDescription, TokenUsage


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


class LLMCompletion(BaseModel):
    content: str
    model_id: str
    provider_model_id: str
    provider_created: int
    usage: TokenUsage
    cost_usd: float | None = None
    duration_ms: int
    result: Any | None = None


def parse_llm_completion(response: Any) -> LLMCompletion:
    response_metadata = getattr(response, "response_metadata", {}) or {}
    usage_metadata = getattr(response, "usage_metadata", {}) or {}
    return LLMCompletion(
        content=response.content,
        model_id=response_metadata["provider_model_id"],
        provider_model_id=response_metadata["provider_model_id"],
        provider_created=response_metadata["provider_created"],
        usage=TokenUsage(
            prompt_tokens=usage_metadata["input_tokens"],
            completion_tokens=usage_metadata["output_tokens"],
            total_tokens=usage_metadata["total_tokens"],
        ),
        cost_usd=response_metadata.get("cost_usd"),
        duration_ms=response_metadata["duration_ms"],
    )


class SceneContext(BaseModel):
    scene_description: SceneDescription
    characters: list[CharacterCard]
    user_character: CharacterCard | None
    messages: list[Message]
    context_data: list[str] = []
