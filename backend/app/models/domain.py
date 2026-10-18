from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

# TODO: move to Enums with methods for subset returning
StoryType = Literal["scene", "choice_driven", "character_driven"]
LLMUsageOperation = Literal[
    "scene_reply",
    "scene_summary",
    "story_generation",
    "choice_generation",
    "character_action",
    "narration",
    "character_memory_update",
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

    def _feature_lines(self) -> list[str]:
        lines: list[str] = []
        for key, value in self.features.items():
            heading = key.replace("_", " ").title()
            lines.append(f"### {heading}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(value)
        return lines

    def to_profile_text(self) -> str:
        return "\n".join(self._feature_lines())

    def to_prompt_text(self) -> str:
        lines: list[str] = [f"## {self.name}", *self._feature_lines()]
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
    character_id: str | None = None

    # TODO: refactor to decrease complexity
    @model_validator(mode="after")
    def validate_references(self) -> "LLMUsage":
        if self.operation in {"scene_reply", "scene_summary", "character_action", "narration"}:
            if self.scene_id is None:
                raise ValueError("scene operations require scene_id")
            if self.step_id is not None:
                raise ValueError("scene operations cannot include step_id")
            if self.operation in {"character_action", "narration"}:
                if self.message_id is None:
                    raise ValueError(f"{self.operation} requires message_id")
                if self.operation == "character_action" and self.character_id is None:
                    raise ValueError("character_action requires character_id")
                if self.operation == "narration" and self.character_id is not None:
                    raise ValueError("narration cannot include character_id")
        elif self.operation == "character_memory_update":
            if self.scene_id is None:
                raise ValueError("character_memory_update requires scene_id")
            if self.character_id is None:
                raise ValueError("character_memory_update requires character_id")
            if self.message_id is not None or self.step_id is not None:
                raise ValueError(
                    "character_memory_update cannot include message_id or step_id"
                )
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


class CharacterDrivenInput(BaseModel):
    author: str | None
    action: str
    guidance: str | None = None


class CharacterDrivenLLMData(BaseModel):
    narrator_model_id: str
    character_model_id: str | None


class CharacterDrivenMessage(BaseModel):
    id: int
    input: CharacterDrivenInput | None = None
    narration: str
    llm_data: CharacterDrivenLLMData


def get_character_driven_turn_type(
    author: str | None, scene_metadata: SceneMetadata
) -> Literal["player", "character"]:
    if author is None or author == scene_metadata.user_character_id:
        return "player"
    return "character"


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
