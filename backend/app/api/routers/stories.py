from fastapi import APIRouter

from app.models.api import ErrorResponse, StoryDetailResponse, StoryListResponse

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=StoryListResponse)
def list_stories():
    return {
        "data": [
            {
                "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
                "title": "The Black Harbor",
            }
        ]
    }


@router.get("/{story_id}", response_model=StoryDetailResponse)
def get_story(story_id: str):
    return {
        "data": {
            "id": "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
            "title": "The Black Harbor",
            "scenes": [
                {"id": 1, "finished": True},
                {"id": 2, "finished": True},
                {"id": 3, "finished": False},
            ],
            "active_scene_id": 3,
        }
    }
