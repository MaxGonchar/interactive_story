from __future__ import annotations

from app.exceptions import NotFoundError
from app.models.domain import Choice, ChoiceDrivenStoryMeta, Step
from app.models.storage import ChoiceDrivenStoryYaml, ChoiceYaml, HistoryYaml, StepYaml
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


class ChoiceDrivenStoryRepository:
    async def get_story_meta(self, story_id: str) -> ChoiceDrivenStoryMeta:
        try:
            data = await yaml_storage.read_yaml(file_paths.story_file(story_id))
        except FileNotFoundError:
            raise NotFoundError(f"Story '{story_id}' not found")

        raw = ChoiceDrivenStoryYaml(**data)
        return ChoiceDrivenStoryMeta(
            id=raw.id,
            title=raw.title,
            writing_style=raw.writing_style,
            plot_directions=raw.plot_directions,
            character_ids=raw.character_ids,
        )

    async def get_history(self, story_id: str) -> list[Step]:
        try:
            data = await yaml_storage.read_yaml(file_paths.history_file(story_id))
        except FileNotFoundError:
            return []

        parsed = HistoryYaml(**data)
        return [_step_from_yaml(s) for s in parsed.steps]

    async def append_step(self, story_id: str, step: Step) -> None:
        steps = await self.get_history(story_id)
        steps.append(step)
        await self._save_history(story_id, steps)

    async def update_step_choices(
        self, story_id: str, step_id: int, choices: list[Choice]
    ) -> None:
        steps = await self.get_history(story_id)
        target = next((s for s in steps if s.id == step_id), None)
        if target is None:
            raise NotFoundError(f"Step '{step_id}' not found")
        target.choices = choices
        await self._save_history(story_id, steps)

    async def update_step_text(self, story_id: str, step_id: int, text: str) -> None:
        steps = await self.get_history(story_id)
        target = next((s for s in steps if s.id == step_id), None)
        if target is None:
            raise NotFoundError(f"Step '{step_id}' not found")
        target.text = text
        await self._save_history(story_id, steps)

    async def truncate_from(self, story_id: str, step_id: int) -> None:
        steps = await self.get_history(story_id)
        kept = [s for s in steps if s.id <= step_id]
        await self._save_history(story_id, kept)

    async def _save_history(self, story_id: str, steps: list[Step]) -> None:
        data = {
            "steps": [
                {
                    "id": s.id,
                    "incoming_choice": (
                        {"action": s.incoming_choice.action, "consequence": s.incoming_choice.consequence}
                        if s.incoming_choice is not None
                        else None
                    ),
                    "text": s.text,
                    "choices": [
                        {"action": c.action, "consequence": c.consequence}
                        for c in s.choices
                    ],
                }
                for s in steps
            ]
        }
        await atomic_write(
            file_paths.history_file(story_id),
            yaml_storage.dump_yaml(data),
        )


def _step_from_yaml(raw: StepYaml) -> Step:
    return Step(
        id=raw.id,
        incoming_choice=(
            Choice(action=raw.incoming_choice.action, consequence=raw.incoming_choice.consequence)
            if raw.incoming_choice is not None
            else None
        ),
        text=raw.text,
        choices=[Choice(action=c.action, consequence=c.consequence) for c in raw.choices],
    )
