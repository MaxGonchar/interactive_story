from fastapi import APIRouter, Depends, Response

from app.api.dependencies import (
    get_character_driven_scene_creation_service,
    get_character_driven_scene_item_service,
    get_character_driven_scene_memory_service,
    get_character_driven_scene_query_service,
    get_character_driven_scene_summary_service,
    get_character_driven_scene_turn_service,
)
from app.models.api import (
    CreateCharacterDrivenSceneRequest,
    CreateCharacterDrivenSceneResponse,
    SceneDescriptionModel,
    CharacterDrivenCharacterActor,
    CharacterDrivenCharacterInput,
    CharacterDrivenLLMDataModel,
    CharacterDrivenPlayerActor,
    CharacterDrivenPlayerInput,
    CharacterDrivenSceneDetail,
    CharacterDrivenSceneDetailResponse,
    CharacterDrivenSceneItem,
    CharacterDrivenSceneItemResponse,
    CharacterDrivenSummaryDraftResponse,
    CharacterMemoryDraftResponse,
    CharacterDrivenTurnRequest,
    CharacterDrivenTurnResponse,
    DeleteCharacterDrivenSceneItemResponse,
    UpdateCharacterDrivenSceneItemRequest,
)
from app.models.domain import (
    CharacterDrivenMessage,
    SceneMetadata,
    get_character_driven_turn_type,
)
from app.services.character_driven_scene_creation_service import (
    CharacterDrivenSceneCreationService,
)
from app.services.character_driven_scene_item_service import (
    CharacterDrivenSceneItemService,
)
from app.services.character_driven_scene_query_service import (
    CharacterDrivenSceneQueryService,
)
from app.services.character_driven_scene_memory_service import (
    CharacterDrivenSceneMemoryService,
)
from app.services.character_driven_scene_summary_service import (
    CharacterDrivenSceneSummaryService,
)
from app.services.character_driven_scene_turn_service import (
    CharacterDrivenSceneTurnService,
)

router = APIRouter(prefix="/stories", tags=["character-play"])


def map_character_driven_item(
    message: CharacterDrivenMessage, metadata: SceneMetadata
) -> CharacterDrivenSceneItem:
    actor = None
    item_input = None
    character_action = None

    if message.input is not None:
        turn_type = get_character_driven_turn_type(message.input.author, metadata)
        if turn_type == "player":
            actor = CharacterDrivenPlayerActor(type="player")
            item_input = CharacterDrivenPlayerInput(action=message.input.action)
        else:
            actor = CharacterDrivenCharacterActor(
                type="character", character_id=message.input.author
            )
            item_input = CharacterDrivenCharacterInput(
                guidance=message.input.guidance
            )
            character_action = message.input.action

    return CharacterDrivenSceneItem(
        id=message.id,
        actor=actor,
        input=item_input,
        character_action=character_action,
        narration=message.narration,
        llm_data=CharacterDrivenLLMDataModel(
            character_model_id=message.llm_data.character_model_id,
            narrator_model_id=message.llm_data.narrator_model_id,
        ),
    )


@router.get(
    "/{story_id}/character-play/scenes/{scene_id}",
    response_model=CharacterDrivenSceneDetailResponse,
)
async def get_scene(
    story_id: str,
    scene_id: int,
    svc: CharacterDrivenSceneQueryService = Depends(
        get_character_driven_scene_query_service
    ),
):
    metadata, messages = await svc.get_scene(story_id, scene_id)
    return {
        "data": CharacterDrivenSceneDetail(
            id=metadata.id,
            finished=metadata.finished,
            user_character_id=metadata.user_character_id,
            character_ids=metadata.character_ids,
            scene_description=SceneDescriptionModel(
                general_scene_guide=metadata.scene_description.general_scene_guide,
                writing_style=metadata.scene_description.writing_style,
            ),
            context=metadata.context,
            scene_summary=metadata.scene_summary,
            items=[map_character_driven_item(message, metadata) for message in messages],
        )
    }


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


@router.post(
    "/{story_id}/character-play/scenes/{scene_id}/turns",
    response_model=CharacterDrivenTurnResponse,
)
async def submit_turn(
    story_id: str,
    scene_id: int,
    request: CharacterDrivenTurnRequest,
    svc: CharacterDrivenSceneTurnService = Depends(
        get_character_driven_scene_turn_service
    ),
):
    metadata, message = await svc.submit_turn(story_id, scene_id, request)
    return {"data": map_character_driven_item(message, metadata)}


@router.post(
    "/{story_id}/character-play/scenes/{scene_id}/turns/{item_id}/replace",
    response_model=CharacterDrivenTurnResponse,
)
async def replace_turn(
    story_id: str,
    scene_id: int,
    item_id: int,
    request: CharacterDrivenTurnRequest,
    svc: CharacterDrivenSceneTurnService = Depends(
        get_character_driven_scene_turn_service
    ),
):
    metadata, message = await svc.replace_turn(story_id, scene_id, item_id, request)
    return {"data": map_character_driven_item(message, metadata)}


@router.put(
    "/{story_id}/character-play/scenes/{scene_id}/items/{item_id}",
    response_model=CharacterDrivenSceneItemResponse,
)
async def edit_item(
    story_id: str,
    scene_id: int,
    item_id: int,
    request: UpdateCharacterDrivenSceneItemRequest,
    svc: CharacterDrivenSceneItemService = Depends(
        get_character_driven_scene_item_service
    ),
):
    metadata, message = await svc.edit_item(
        story_id, scene_id, item_id, request.narration
    )
    return {"data": map_character_driven_item(message, metadata)}


@router.delete(
    "/{story_id}/character-play/scenes/{scene_id}/items/{item_id}",
    response_model=DeleteCharacterDrivenSceneItemResponse,
)
async def delete_item(
    story_id: str,
    scene_id: int,
    item_id: int,
    svc: CharacterDrivenSceneItemService = Depends(
        get_character_driven_scene_item_service
    ),
):
    await svc.delete_item(story_id, scene_id, item_id)
    return {"success": True}


@router.get(
    "/{story_id}/character-play/scenes/{scene_id}/summary/draft",
    response_model=CharacterDrivenSummaryDraftResponse,
)
async def get_summary_draft(
    story_id: str,
    scene_id: int,
    response: Response,
    svc: CharacterDrivenSceneSummaryService = Depends(
        get_character_driven_scene_summary_service
    ),
):
    summary = await svc.draft(story_id, scene_id)
    response.headers["Cache-Control"] = "no-store"
    return {"data": {"summary": summary}}


@router.get(
    "/{story_id}/character-play/scenes/{scene_id}/characters/{character_id}/memory/draft",
    response_model=CharacterMemoryDraftResponse,
)
async def get_memory_draft(
    story_id: str,
    scene_id: int,
    character_id: str,
    response: Response,
    svc: CharacterDrivenSceneMemoryService = Depends(
        get_character_driven_scene_memory_service
    ),
):
    memory_updates = await svc.draft(story_id, scene_id, character_id)
    response.headers["Cache-Control"] = "no-store"
    return {"data": {"character_id": character_id, "memory_updates": memory_updates}}
