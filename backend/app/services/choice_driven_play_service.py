from __future__ import annotations

import asyncio
import logging

from app.exceptions import NoStepsError
from app.llm.choice_engine_client import ChoiceEngineClient
from app.llm.story_engine_client import StoryEngineClient
from app.models.domain import Choice, ChoiceDrivenStoryMeta, Step
from app.repositories.character_repository import CharacterRepository
from app.repositories.choice_driven_story_repository import ChoiceDrivenStoryRepository

_PARAGRAPH_WINDOW = 10

logger = logging.getLogger(__name__)


class ChoiceDrivenPlayService:
    def __init__(
        self,
        repo: ChoiceDrivenStoryRepository,
        character_repo: CharacterRepository,
        choice_engine_client: ChoiceEngineClient,
        story_engine_client: StoryEngineClient,
    ) -> None:
        self._repo = repo
        self._character_repo = character_repo
        self._choice_engine_client = choice_engine_client
        self._story_engine_client = story_engine_client

    async def get_play_state(self, story_id: str) -> list[Step]:
        return await self._repo.get_history(story_id)

    async def get_story_state(self, story_id: str) -> tuple[ChoiceDrivenStoryMeta, list[Step]]:
        meta, steps = await asyncio.gather(
            self._repo.get_story_meta(story_id),
            self.get_play_state(story_id),
        )
        return meta, steps

    async def generate_choices(self, story_id: str) -> list[Choice]:
        logger.info(f"Generating choices story_id={story_id}")
        meta, steps = await asyncio.gather(
            self._repo.get_story_meta(story_id),
            self._repo.get_history(story_id),
        )

        if not steps:
            raise NoStepsError()

        user_character, supporting_characters = await self._load_character_context(
            story_id,
            meta.user_character_id,
            meta.character_ids,
        )
        story_text = "\n\n".join(s.text for s in steps)

        results: list[list[Choice]] = list(
            await asyncio.gather(
                *[
                    self._choice_engine_client.invoke(
                        story_text,
                        plot_direction=direction,
                        user_character=user_character,
                        supporting_characters=supporting_characters,
                    )
                    for direction in meta.plot_directions
                ]
            )
        )

        choices = [choice for batch in results for choice in batch]
        await self._repo.update_step_choices(story_id, steps[-1].id, choices)
        return choices

    async def regenerate_choices(self, story_id: str) -> list[Choice]:
        logger.info(f"Regenerating choices story_id={story_id}")
        steps = await self._repo.get_history(story_id)

        if not steps:
            raise NoStepsError()

        await self._repo.update_step_choices(story_id, steps[-1].id, [])
        return await self.generate_choices(story_id)

    async def select_choice(self, story_id: str, choice: Choice) -> Step:
        logger.info(f"Selecting choice story_id={story_id}")
        meta, steps = await asyncio.gather(
            self._repo.get_story_meta(story_id),
            self._repo.get_history(story_id),
        )

        user_character, supporting_characters = await self._load_character_context(
            story_id,
            meta.user_character_id,
            meta.character_ids,
        )
        window = steps[-_PARAGRAPH_WINDOW:]
        story_text = "\n\n".join(s.text for s in window)

        reply = await self._story_engine_client.invoke(
            story_text,
            choice.action,
            choice.consequence,
            user_character=user_character,
            supporting_characters=supporting_characters,
            writing_style=meta.writing_style,
        )

        last_id = steps[-1].id if steps else 0
        new_step = Step(
            id=last_id + 1,
            incoming_choice=choice,
            text=reply,
            choices=[],
        )
        await self._repo.append_step(story_id, new_step)
        return new_step

    async def edit_step_text(self, story_id: str, step_id: int, text: str) -> Step:
        logger.info(f"Editing step text story_id={story_id} step_id={step_id}")
        await self._repo.update_step_text(story_id, step_id, text)
        steps = await self._repo.get_history(story_id)
        target = next((s for s in steps if s.id == step_id), None)
        if target is None:
            raise KeyError(step_id)
        return target

    async def return_to_step(self, story_id: str, step_id: int) -> int:
        logger.info(f"Returning to step story_id={story_id} step_id={step_id}")
        await self._repo.truncate_from(story_id, step_id)
        return step_id

    async def _load_character_context(
        self,
        story_id: str,
        user_character_id: str,
        supporting_character_ids: list[str],
    ):
        user_character, supporting_characters = await asyncio.gather(
            self._character_repo.get_character(story_id, user_character_id),
            self._character_repo.get_characters(
                story_id,
                [cid for cid in supporting_character_ids if cid != user_character_id],
            ),
        )
        return user_character, supporting_characters
