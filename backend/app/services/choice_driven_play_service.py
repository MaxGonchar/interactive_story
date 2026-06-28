from __future__ import annotations

import asyncio

from app.llm.choice_engine_client import ChoiceEngineClient
from app.llm.story_engine_client import StoryEngineClient
from app.models.domain import Choice, Step
from app.repositories.character_repository import CharacterRepository
from app.repositories.choice_driven_story_repository import ChoiceDrivenStoryRepository

_PARAGRAPH_WINDOW = 10


class ChoiceDrivenPlayService:
    def __init__(
        self,
        repo: ChoiceDrivenStoryRepository,
        character_repo: CharacterRepository,
    ) -> None:
        self._repo = repo
        self._character_repo = character_repo

    async def get_play_state(self, story_id: str) -> list[Step]:
        return await self._repo.get_history(story_id)

    async def generate_choices(self, story_id: str) -> list[Choice]:
        meta, steps = await asyncio.gather(
            self._repo.get_story_meta(story_id),
            self._repo.get_history(story_id),
        )

        if not steps:
            raise ValueError("no_steps")

        characters = await self._character_repo.get_characters(story_id, meta.character_ids)
        story_text = "\n\n".join(s.text for s in steps)

        results: list[list[Choice]] = list(
            await asyncio.gather(
                *[
                    ChoiceEngineClient(direction, characters).invoke(story_text)
                    for direction in meta.plot_directions
                ]
            )
        )

        choices = [choice for batch in results for choice in batch]
        await self._repo.update_step_choices(story_id, steps[-1].id, choices)
        return choices

    async def regenerate_choices(self, story_id: str) -> list[Choice]:
        steps = await self._repo.get_history(story_id)

        if not steps:
            raise ValueError("no_steps")

        await self._repo.update_step_choices(story_id, steps[-1].id, [])
        return await self.generate_choices(story_id)

    async def select_choice(self, story_id: str, choice: Choice) -> Step:
        meta, steps = await asyncio.gather(
            self._repo.get_story_meta(story_id),
            self._repo.get_history(story_id),
        )

        characters = await self._character_repo.get_characters(story_id, meta.character_ids)
        window = steps[-_PARAGRAPH_WINDOW:]
        story_text = "\n\n".join(s.text for s in window)

        reply = await StoryEngineClient(characters, meta.writing_style).invoke(
            story_text, choice.action, choice.consequence
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
        await self._repo.update_step_text(story_id, step_id, text)
        steps = await self._repo.get_history(story_id)
        target = next((s for s in steps if s.id == step_id), None)
        if target is None:
            raise KeyError(step_id)
        return target

    async def return_to_step(self, story_id: str, step_id: int) -> int:
        await self._repo.truncate_from(story_id, step_id)
        return step_id
