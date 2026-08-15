from __future__ import annotations

from fastapi import Depends

from app.llm.choice_engine_client import ChoiceEngineClient
from app.llm.scene_llm_client import SceneLLMClient
from app.llm.story_engine_client import StoryEngineClient
from app.repositories.character_repository import CharacterRepository
from app.repositories.choice_driven_story_repository import ChoiceDrivenStoryRepository
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository
from app.services.choice_driven_play_service import ChoiceDrivenPlayService
from app.llm.summarize_llm_client import SummarizeLLMClient
from app.services.scene_creation_service import SceneCreationService
from app.services.scene_lifecycle_service import SceneLifecycleService
from app.services.scene_message_service import SceneMessageService
from app.services.scene_play_service import ScenePlayService
from app.services.scene_query_service import SceneQueryService
from app.services.scene_summarize_service import SceneSummarizeService
from app.services.story_query_service import StoryQueryService


def get_story_repository() -> StoryRepository:
    return StoryRepository()


def get_scene_repository() -> SceneRepository:
    return SceneRepository()


def get_character_repository() -> CharacterRepository:
    return CharacterRepository()


def get_scene_llm_client() -> SceneLLMClient:
    return SceneLLMClient()


def get_story_query_service(
    repo: StoryRepository = Depends(get_story_repository),
) -> StoryQueryService:
    return StoryQueryService(repo)


def get_scene_query_service(
    story_repo: StoryRepository = Depends(get_story_repository),
    scene_repo: SceneRepository = Depends(get_scene_repository),
) -> SceneQueryService:
    return SceneQueryService(story_repo, scene_repo)


def get_scene_play_service(
    scene_repo: SceneRepository = Depends(get_scene_repository),
    character_repo: CharacterRepository = Depends(get_character_repository),
    llm_client: SceneLLMClient = Depends(get_scene_llm_client),
) -> ScenePlayService:
    return ScenePlayService(scene_repo, character_repo, llm_client)


def get_scene_message_service(
    scene_repo: SceneRepository = Depends(get_scene_repository),
) -> SceneMessageService:
    return SceneMessageService(scene_repo)


def get_scene_lifecycle_service(
    scene_repo: SceneRepository = Depends(get_scene_repository),
) -> SceneLifecycleService:
    return SceneLifecycleService(scene_repo)


def get_scene_creation_service(
    story_repo: StoryRepository = Depends(get_story_repository),
    scene_repo: SceneRepository = Depends(get_scene_repository),
) -> SceneCreationService:
    return SceneCreationService(story_repo, scene_repo)


def get_summarize_llm_client() -> SummarizeLLMClient:
    return SummarizeLLMClient()


def get_scene_summarize_service(
    scene_repo: SceneRepository = Depends(get_scene_repository),
    llm_client: SummarizeLLMClient = Depends(get_summarize_llm_client),
) -> SceneSummarizeService:
    return SceneSummarizeService(scene_repo, llm_client)


def get_choice_driven_story_repository() -> ChoiceDrivenStoryRepository:
    return ChoiceDrivenStoryRepository()


def get_choice_engine_client() -> ChoiceEngineClient:
    return ChoiceEngineClient()


def get_story_engine_client() -> StoryEngineClient:
    return StoryEngineClient()


def get_choice_driven_play_service(
    repo: ChoiceDrivenStoryRepository = Depends(get_choice_driven_story_repository),
    character_repo: CharacterRepository = Depends(get_character_repository),
    choice_engine_client: ChoiceEngineClient = Depends(get_choice_engine_client),
    story_engine_client: StoryEngineClient = Depends(get_story_engine_client),
) -> ChoiceDrivenPlayService:
    return ChoiceDrivenPlayService(
        repo=repo,
        character_repo=character_repo,
        choice_engine_client=choice_engine_client,
        story_engine_client=story_engine_client,
    )
