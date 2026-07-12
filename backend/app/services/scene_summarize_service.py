from __future__ import annotations

from app.exceptions import SceneFinishedError
from app.llm.summarize_llm_client import SummarizeLLMClient
from app.repositories.scene_repository import SceneRepository

_MAX_CONTEXT_ITEMS = 50


class SceneSummarizeService:
    def __init__(
        self,
        scene_repo: SceneRepository,
        llm_client: SummarizeLLMClient,
    ) -> None:
        self._scene_repo = scene_repo
        self._llm_client = llm_client

    async def summarize(self, story_id: str, scene_id: int) -> list[str]:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        messages = await self._scene_repo.get_messages(story_id, scene_id)

        previous_summary = (metadata.context or [])[-_MAX_CONTEXT_ITEMS:]

        scene_content = "\n\n".join(
            f"{m.role}:\n{m.content}" for m in messages
        )

        return await self._llm_client.invoke(previous_summary, scene_content)
