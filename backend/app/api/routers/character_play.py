from fastapi import APIRouter, Depends

from app.api.dependencies import get_character_driven_scene_creation_service
from app.models.api import (
    CreateCharacterDrivenSceneRequest,
    CreateCharacterDrivenSceneResponse,
)
from app.services.character_driven_scene_creation_service import (
    CharacterDrivenSceneCreationService,
)

router = APIRouter(prefix="/stories", tags=["character-play"])


@router.post(
    "/{story_id}/character-play/scenes",
    response_model=CreateCharacterDrivenSceneResponse,
    status_code=201,
)
async def create_scene(
    story_id: str,
    request: CreateCharacterDrivenSceneRequest,
    svc: CharacterDrivenSceneCreationService = Depends(
        get_character_driven_scene_creation_service
    ),
):
    scene_ref = await svc.create(
        story_id=story_id,
        user_character_id=request.user_character_id,
        character_ids=request.character_ids,
        context=request.context,
        general_scene_guide=request.general_scene_guide,
        writing_style=request.writing_style,
        first_message=request.first_message,
        character_model_id=request.character_model_id,
        narrator_model_id=request.narrator_model_id,
    )
    return {"data": {"id": scene_ref.id, "finished": scene_ref.finished}}
