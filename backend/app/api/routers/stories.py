from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_story_query_service
from app.models.api import StoryDetailResponse, StoryListResponse
from app.services.story_query_service import StoryQueryService

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=StoryListResponse)
async def list_stories(svc: StoryQueryService = Depends(get_story_query_service)):
    stories = await svc.list_stories()
    return {"data": [{"id": s.id, "title": s.title} for s in stories]}


@router.get("/{story_id}", response_model=StoryDetailResponse)
async def get_story(
    story_id: str,
    svc: StoryQueryService = Depends(get_story_query_service),
):
    try:
        story = await svc.get_story(story_id)
    except KeyError:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": f"Story '{story_id}' not found"}},
        )
    return {
        "data": {
            "id": story.id,
            "title": story.title,
            "user_character_id": story.user_character_id,
            "scenes": [{"id": s.id, "finished": s.finished} for s in story.scenes],
            "active_scene_id": story.active_scene_id,
        }
    }
