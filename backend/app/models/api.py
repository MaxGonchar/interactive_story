from pydantic import BaseModel, Field


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


class StoryListResponse(BaseModel):
    data: list[StoryListItem]


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
    active_scene_id: int


class StoryDetailResponse(BaseModel):
    data: StoryDetail


# ---------------------------------------------------------------------------
# Scene detail  —  GET /api/stories/{story_id}/scenes/{scene_id}
# ---------------------------------------------------------------------------


class SceneDescriptionModel(BaseModel):
    entry_point: str
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
    scene_summary: str | None
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
# Finish scene  —  POST /api/stories/{story_id}/scenes/{scene_id}/finish
# ---------------------------------------------------------------------------


class FinishSceneRequest(BaseModel):
    scene_summary: str = Field(min_length=1, max_length=2000)


class FinishedSceneData(BaseModel):
    id: int
    finished: bool
    scene_summary: str


class FinishSceneResponse(BaseModel):
    data: FinishedSceneData
