from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import (
    get_scene_lifecycle_service,
    get_scene_message_service,
    get_scene_play_service,
    get_scene_query_service,
)
from app.models.api import (
    DeleteMessageResponse,
    FinishSceneRequest,
    FinishSceneResponse,
    PlayRequest,
    PlayResponse,
    SceneDetailResponse,
    UpdateMessageRequest,
    UpdateMessageResponse,
    RegenerateResponse,
)
from app.services.scene_lifecycle_service import SceneLifecycleService
from app.services.scene_message_service import SceneMessageService
from app.services.scene_play_service import ScenePlayService
from app.services.scene_query_service import SceneQueryService

router = APIRouter(prefix="/stories", tags=["scenes"])


@router.get(
    "/{story_id}/scenes/{scene_id}",
    response_model=SceneDetailResponse,
)
async def get_scene(
    story_id: str,
    scene_id: int,
    svc: SceneQueryService = Depends(get_scene_query_service),
):
    try:
        metadata, messages = await svc.get_scene(story_id, scene_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Scene '{scene_id}' not found"}},
        )
    return {
        "data": {
            "id": metadata.id,
            "finished": metadata.finished,
            "scene_description": {
                "entry_point": metadata.scene_description.entry_point,
                "general_scene_guide": metadata.scene_description.general_scene_guide,
                "writing_style": metadata.scene_description.writing_style,
            },
            "scene_summary": "\n".join(metadata.scene_summary) if metadata.scene_summary else None,
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
    try:
        user_msg, assistant_msg = await svc.play(story_id, scene_id, request.content)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Scene '{scene_id}' not found"}},
        )
    except ValueError:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "scene_finished", "message": "Scene is already finished"}},
        )
    except Exception:
        return JSONResponse(
            status_code=502,
            content={"error": {"code": "llm_error", "message": "LLM request failed"}},
        )
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
    try:
        message = await svc.edit_message(story_id, scene_id, message_id, request.content)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Message '{message_id}' not found"}},
        )
    except ValueError:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "scene_finished", "message": "Scene is already finished"}},
        )
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
    try:
        await svc.delete_message(story_id, scene_id, message_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Message '{message_id}' not found"}},
        )
    except ValueError:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "scene_finished", "message": "Scene is already finished"}},
        )
    return {"success": True}


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
    try:
        await svc.finish_scene(story_id, scene_id, request.scene_summary)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Scene '{scene_id}' not found"}},
        )
    except ValueError:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "scene_finished", "message": "Scene is already finished"}},
        )
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
    try:
        assistant_msg = await svc.regenerate(story_id, scene_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Scene '{scene_id}' not found"}},
        )
    except ValueError as e:
        if str(e) == "scene_finished":
            return JSONResponse(
                status_code=409,
                content={"error": {"code": "scene_finished", "message": "Scene is already finished"}},
            )
        elif str(e) == "no_assistant_message":
            return JSONResponse(
                status_code=409,
                content={"error": {"code": "no_assistant_message", "message": "No assistant message to regenerate"}},
            )
        else:
            return JSONResponse(
                status_code=502,
                content={"error": {"code": "llm_error", "message": "LLM request failed"}},
            )
    except Exception:
        return JSONResponse(
            status_code=502,
            content={"error": {"code": "llm_error", "message": "LLM request failed"}},
        )
    return {"data": {"assistant_message": {"id": assistant_msg.id, "role": assistant_msg.role, "content": assistant_msg.content}}}
