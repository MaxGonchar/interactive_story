from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

StoryType = Literal["scene", "choice_driven"]
LLMUsageOperation = Literal[
    "scene_reply", "scene_summary", "story_generation", "choice_generation"
]


class StoryIndexItem(BaseModel):
    id: str
    title: str
    created_at: str
    type: StoryType


class SceneRef(BaseModel):
    id: int
    finished: bool


class StoryMeta(BaseModel):
    id: str
    title: str
    scenes: list[SceneRef]
    active_scene_id: int | None
    type: StoryType = "scene"


class CharacterCard(BaseModel):
    id: str
    name: str
    features: dict[str, str | list[str]] = {}
    memory: list[str] = []

    def to_prompt_text(self) -> str:
        lines: list[str] = [f"## {self.name}"]
        for key, value in self.features.items():
            heading = key.replace("_", " ").title()
            lines.append(f"### {heading}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(value)
        if self.memory:
            lines.append("### Memory")
            for entry in self.memory:
                lines.append(f"- {entry}")
        return "\n".join(lines)


class SceneDescription(BaseModel):
    general_scene_guide: str
    writing_style: str


class LLMData(BaseModel):
    model_id: str


class TokenUsage(BaseModel):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class LLMUsage(BaseModel):
    id: UUID
    operation: LLMUsageOperation
    model_id: str
    provider_model_id: str
    provider_created: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    usage: TokenUsage
    cost_usd: float | None = Field(default=None, ge=0)
    scene_id: int | None = Field(default=None, ge=1)
    message_id: int | None = Field(default=None, ge=1)
    step_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_references(self) -> "LLMUsage":
        if self.operation in {"scene_reply", "scene_summary"}:
            if self.scene_id is None:
                raise ValueError("scene operations require scene_id")
            if self.step_id is not None:
                raise ValueError("scene operations cannot include step_id")
        elif self.operation == "choice_generation":
            if self.step_id is None:
                raise ValueError("choice_generation requires step_id")
            if self.scene_id is not None or self.message_id is not None:
                raise ValueError("choice_generation cannot include scene references")
        elif any(
            reference is not None
            for reference in (self.scene_id, self.message_id, self.step_id)
        ):
            raise ValueError("story_generation cannot include content references")

        if self.operation == "scene_summary" and self.message_id is not None:
            raise ValueError("scene_summary cannot include message_id")
        return self


class SceneMetadata(BaseModel):
    id: int
    story_id: str
    character_ids: list[str]
    user_character_id: str | None
    finished: bool
    scene_description: SceneDescription
    scene_summary: list[str] | None = None
    context: list[str] | None = None


class Message(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str
    llm_data: LLMData | None = None


class ModelMetadata(BaseModel):
    id: str
    name: str
    provider_model_id: str


class ModelRegistry(BaseModel):
    models: dict[str, ModelMetadata]
    default_model_id: str


class Choice(BaseModel):
    action: str
    consequence: str


class Step(BaseModel):
    id: int
    incoming_choice: Choice | None
    text: str
    choices: list[Choice]


class ChoiceDrivenStoryMeta(BaseModel):
    id: str
    title: str
    writing_style: str
    plot_directions: list[str]
    user_character_id: str
    character_ids: list[str]
