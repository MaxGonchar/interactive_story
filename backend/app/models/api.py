from typing import Annotated

from pydantic import BaseModel, Field, model_validator

from app.models.domain import StoryType


# ---------------------------------------------------------------------------
# Error models
# ---------------------------------------------------------------------------


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ---------------------------------------------------------------------------
# Stories list  —  GET /api/stories
# ---------------------------------------------------------------------------


class StoryListItem(BaseModel):
    id: str
    title: str
    type: StoryType


class StoryListResponse(BaseModel):
    data: list[StoryListItem]


# ---------------------------------------------------------------------------
# Character list  —  GET /api/stories/{story_id}/characters
# ---------------------------------------------------------------------------


class CharacterListItem(BaseModel):
    id: str
    name: str


class CharacterListResponse(BaseModel):
    data: list[CharacterListItem]


# ---------------------------------------------------------------------------
# Story detail  —  GET /api/stories/{story_id}
# ---------------------------------------------------------------------------


class SceneListItem(BaseModel):
    id: int
    finished: bool


class StoryDetail(BaseModel):
    id: str
    title: str
    scenes: list[SceneListItem]
    active_scene_id: int | None


class StoryDetailResponse(BaseModel):
    data: StoryDetail


# ---------------------------------------------------------------------------
# Scene detail  —  GET /api/stories/{story_id}/scenes/{scene_id}
# ---------------------------------------------------------------------------


class SceneDescriptionModel(BaseModel):
    general_scene_guide: str
    writing_style: str


class MessageModel(BaseModel):
    id: int
    role: str
    content: str


class SceneDetail(BaseModel):
    id: int
    finished: bool
    scene_description: SceneDescriptionModel
    scene_summary: list[str] | None
    context: list[str] | None
    messages: list[MessageModel]


class SceneDetailResponse(BaseModel):
    data: SceneDetail


# ---------------------------------------------------------------------------
# Play  —  POST /api/stories/{story_id}/scenes/{scene_id}/play
# ---------------------------------------------------------------------------


class PlayRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class PlayData(BaseModel):
    user_message: MessageModel
    assistant_message: MessageModel


class PlayResponse(BaseModel):
    data: PlayData


# ---------------------------------------------------------------------------
# Update message  —  PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}
# ---------------------------------------------------------------------------


class UpdateMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class UpdateMessageResponse(BaseModel):
    data: MessageModel


# ---------------------------------------------------------------------------
# Delete message  —  DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}
# ---------------------------------------------------------------------------


class DeleteMessageResponse(BaseModel):
    success: bool


# ---------------------------------------------------------------------------
# Regenerate  —  POST /api/stories/{story_id}/scenes/{scene_id}/regenerate
# ---------------------------------------------------------------------------

class RegenerateData(BaseModel):
    assistant_message: MessageModel

class RegenerateResponse(BaseModel):
    data: RegenerateData


# ---------------------------------------------------------------------------
# Scene creation  —  POST /api/stories/{story_id}/scenes
# ---------------------------------------------------------------------------


class CreateSceneRequest(BaseModel):
    user_character_id: str
    character_ids: list[str] = []
    context: list[str] = Field(min_length=1)
    general_scene_guide: str
    writing_style: str
    first_message: str

    @model_validator(mode="after")
    def user_character_not_in_character_ids(self) -> "CreateSceneRequest":
        if self.user_character_id in self.character_ids:
            raise ValueError(
                "user_character_id must not appear in character_ids"
            )
        return self


class CreateSceneResponse(BaseModel):
    data: SceneListItem


# ---------------------------------------------------------------------------
# Finish scene  —  POST /api/stories/{story_id}/scenes/{scene_id}/finish
# ---------------------------------------------------------------------------


class FinishSceneRequest(BaseModel):
    scene_summary: list[Annotated[str, Field(min_length=1)]] = Field(min_length=1, max_length=100)


class FinishedSceneData(BaseModel):
    id: int
    finished: bool
    scene_summary: list[str]


class FinishSceneResponse(BaseModel):
    data: FinishedSceneData


# ---------------------------------------------------------------------------
# Summarize scene  —  GET /api/stories/{story_id}/scenes/{scene_id}/summarize
# ---------------------------------------------------------------------------


class SummarizeSceneData(BaseModel):
    summary: list[str]


class SummarizeSceneResponse(BaseModel):
    data: SummarizeSceneData


# ---------------------------------------------------------------------------
# Choice-Driven Play  —  GET /api/stories/{story_id}/choice-play
# ---------------------------------------------------------------------------


class ChoiceModel(BaseModel):
    action: str
    consequence: str


class StepModel(BaseModel):
    id: int
    incoming_choice: ChoiceModel | None
    text: str
    choices: list[ChoiceModel]


class ChoiceDrivenPlayData(BaseModel):
    id: str
    title: str
    steps: list[StepModel]


class ChoiceDrivenPlayResponse(BaseModel):
    data: ChoiceDrivenPlayData


# ---------------------------------------------------------------------------
# Generate / Regenerate Choices
# POST /api/stories/{story_id}/choice-play/generate-choices
# POST /api/stories/{story_id}/choice-play/regenerate-choices
# ---------------------------------------------------------------------------


class GenerateChoicesData(BaseModel):
    choices: list[ChoiceModel]


class GenerateChoicesResponse(BaseModel):
    data: GenerateChoicesData


# ---------------------------------------------------------------------------
# Select Choice  —  POST /api/stories/{story_id}/choice-play/select-choice
# ---------------------------------------------------------------------------


class SelectChoiceRequest(BaseModel):
    action: str
    consequence: str


class SelectChoiceResponse(BaseModel):
    data: StepModel


# ---------------------------------------------------------------------------
# Edit Step  —  PATCH /api/stories/{story_id}/choice-play/steps/{step_id}
# ---------------------------------------------------------------------------


class EditStepRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class EditStepData(BaseModel):
    id: int
    text: str


class EditStepResponse(BaseModel):
    data: EditStepData


# ---------------------------------------------------------------------------
# Return To Step  —  DELETE /api/stories/{story_id}/choice-play/steps/{step_id}/forward
# ---------------------------------------------------------------------------


class ReturnToStepData(BaseModel):
    step_id: int


class ReturnToStepResponse(BaseModel):
    data: ReturnToStepData
