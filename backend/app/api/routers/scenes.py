from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_scene_creation_service,
    get_scene_lifecycle_service,
    get_scene_message_service,
    get_scene_play_service,
    get_scene_query_service,
    get_scene_summarize_service,
)
from app.models.api import (
    CreateSceneRequest,
    CreateSceneResponse,
    DeleteMessageResponse,
    FinishSceneRequest,
    FinishSceneResponse,
    PlayRequest,
    PlayResponse,
    SceneDetailResponse,
    SummarizeSceneResponse,
    UpdateMessageRequest,
    UpdateMessageResponse,
    RegenerateResponse,
)
from app.services.scene_creation_service import SceneCreationService
from app.services.scene_lifecycle_service import SceneLifecycleService
from app.services.scene_message_service import SceneMessageService
from app.services.scene_play_service import ScenePlayService
from app.services.scene_query_service import SceneQueryService
from app.services.scene_summarize_service import SceneSummarizeService

router = APIRouter(prefix="/stories", tags=["scenes"])


@router.post(
    "/{story_id}/scenes",
    response_model=CreateSceneResponse,
    status_code=201,
)
async def create_scene(
    story_id: str,
    request: CreateSceneRequest,
    svc: SceneCreationService = Depends(get_scene_creation_service),
):
    scene_ref = await svc.create(
        story_id=story_id,
        user_character_id=request.user_character_id,
        character_ids=request.character_ids,
        context=request.context,
        general_scene_guide=request.general_scene_guide,
        writing_style=request.writing_style,
        first_message=request.first_message,
    )
    return {"data": {"id": scene_ref.id, "finished": scene_ref.finished}}


@router.get(
    "/{story_id}/scenes/{scene_id}",
    response_model=SceneDetailResponse,
)
async def get_scene(
    story_id: str,
    scene_id: int,
    svc: SceneQueryService = Depends(get_scene_query_service),
):
    metadata, messages = await svc.get_scene(story_id, scene_id)
    return {
        "data": {
            "id": metadata.id,
            "finished": metadata.finished,
            "scene_description": {
                "general_scene_guide": metadata.scene_description.general_scene_guide,
                "writing_style": metadata.scene_description.writing_style,
            },
            "scene_summary": metadata.scene_summary or None,
            "messages": [{"id": m.id, "role": m.role, "content": m.content} for m in messages],
        }
    }


@router.post(
    "/{story_id}/scenes/{scene_id}/play",
    response_model=PlayResponse,
)
async def play(
    story_id: str,
    scene_id: int,
    request: PlayRequest,
    svc: ScenePlayService = Depends(get_scene_play_service),
):
    user_msg, assistant_msg = await svc.play(story_id, scene_id, request.content)
    return {
        "data": {
            "user_message": {"id": user_msg.id, "role": user_msg.role, "content": user_msg.content},
            "assistant_message": {"id": assistant_msg.id, "role": assistant_msg.role, "content": assistant_msg.content},
        }
    }


@router.put(
    "/{story_id}/scenes/{scene_id}/messages/{message_id}",
    response_model=UpdateMessageResponse,
)
async def edit_message(
    story_id: str,
    scene_id: int,
    message_id: int,
    request: UpdateMessageRequest,
    svc: SceneMessageService = Depends(get_scene_message_service),
):
    message = await svc.edit_message(story_id, scene_id, message_id, request.content)
    return {"data": {"id": message.id, "role": message.role, "content": message.content}}


@router.delete(
    "/{story_id}/scenes/{scene_id}/messages/{message_id}",
    response_model=DeleteMessageResponse,
)
async def delete_message(
    story_id: str,
    scene_id: int,
    message_id: int,
    svc: SceneMessageService = Depends(get_scene_message_service),
):
    await svc.delete_message(story_id, scene_id, message_id)
    return {"success": True}


@router.get(
    "/{story_id}/scenes/{scene_id}/summarize",
    response_model=SummarizeSceneResponse,
)
async def summarize_scene(
    story_id: str,
    scene_id: int,
    svc: SceneSummarizeService = Depends(get_scene_summarize_service),
):
    summary = await svc.summarize(story_id, scene_id)
    return {"data": {"summary": summary}}


@router.post(
    "/{story_id}/scenes/{scene_id}/finish",
    response_model=FinishSceneResponse,
)
async def finish_scene(
    story_id: str,
    scene_id: int,
    request: FinishSceneRequest,
    svc: SceneLifecycleService = Depends(get_scene_lifecycle_service),
):
    await svc.finish_scene(story_id, scene_id, request.scene_summary)
    return {
        "data": {
            "id": scene_id,
            "finished": True,
            "scene_summary": request.scene_summary,
        }
    }


@router.post(
    "/{story_id}/scenes/{scene_id}/regenerate",
    response_model=RegenerateResponse,
)
async def regenerate_assistant_message(
    story_id: str,
    scene_id: int,
    svc: ScenePlayService = Depends(get_scene_play_service),
):
    assistant_msg = await svc.regenerate(story_id, scene_id)
    return {"data": {"assistant_message": {"id": assistant_msg.id, "role": assistant_msg.role, "content": assistant_msg.content}}}
