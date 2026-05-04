from fastapi import APIRouter

from app.models.api import ErrorResponse, PlayRequest, PlayResponse, SceneDetailResponse

router = APIRouter(prefix="/stories", tags=["scenes"])


@router.get(
    "/{story_id}/scenes/{scene_id}",
    response_model=SceneDetailResponse,
)
def get_scene(story_id: str, scene_id: int):
    return {
        "data": {
            "id": 3,
            "finished": False,
            "scene_description": {
                "entry_point": "Fog rolls over the black harbor as bells ring in distance.",
                "general_scene_guide": "Keep tension rising with small discoveries and choices.",
                "writing_style": "Cinematic, sensory details, concise dialog turns.",
            },
            "scene_summary": None,
            "messages": [
                {
                    "id": 1,
                    "role": "assistant",
                    "content": "You step into the foggy harbor...",
                },
                {
                    "id": 2,
                    "role": "user",
                    "content": "I look for the nearest light source.",
                },
            ],
        }
    }


@router.post(
    "/{story_id}/scenes/{scene_id}/play",
    response_model=PlayResponse,
)
def play(story_id: str, scene_id: int, request: PlayRequest):
    return {
        "data": {
            "user_message": {"id": 2, "role": "user", "content": request.content},
            "assistant_message": {
                "id": 3,
                "role": "assistant",
                "content": "A lantern swings near a wooden post...",
            },
        }
    }
