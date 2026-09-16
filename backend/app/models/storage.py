from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.domain import LLMUsageOperation, StoryType


# ---------------------------------------------------------------------------
# Story metadata  —  data/stories/<story_id>/story.yaml
# ---------------------------------------------------------------------------


class StoryYaml(BaseModel):
    title: str
    type: StoryType
    created_at: str


# ---------------------------------------------------------------------------
# Scene metadata  —  data/stories/<story_id>/scenes/<scene_id>/metadata.yaml
# ---------------------------------------------------------------------------


class SceneDescriptionYaml(BaseModel):
    general_scene_guide: str
    writing_style: str


class LLMDataYaml(BaseModel):
    model_id: str


class TokenUsageYaml(BaseModel):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class LLMUsageYaml(BaseModel):
    id: UUID
    operation: LLMUsageOperation
    model_id: str
    provider_model_id: str
    provider_created: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    usage: TokenUsageYaml
    cost_usd: float | None = Field(default=None, ge=0)
    scene_id: int | None = Field(default=None, ge=1)
    message_id: int | None = Field(default=None, ge=1)
    step_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_references(self) -> "LLMUsageYaml":
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


class LLMUsageDocumentYaml(BaseModel):
    calls: list[LLMUsageYaml]


class SceneMetadataYaml(BaseModel):
    finished: bool = False
    character_ids: list[str]
    user_character_id: str | None
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
    llm_data: LLMDataYaml | None = None


class MessagesYaml(BaseModel):
    messages: list[MessageYaml]


# ---------------------------------------------------------------------------
# Model registry — data/models.yaml
# ---------------------------------------------------------------------------


class ModelYaml(BaseModel):
    name: str = Field(min_length=1)
    provider_model_id: str = Field(alias="providerModelID", min_length=1)
    default: bool = False

    model_config = ConfigDict(populate_by_name=True)


class ModelRegistryYaml(BaseModel):
    models: dict[str, ModelYaml]


# ---------------------------------------------------------------------------
# Choice-driven story  —  data/stories/<story_id>/story.yaml (choice_driven)
# ---------------------------------------------------------------------------


class ChoiceDrivenStoryYaml(BaseModel):
    title: str
    type: Literal["choice_driven"]
    created_at: str
    user_character_id: str
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
