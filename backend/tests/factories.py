from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from app.exceptions import NotFoundError
from app.models.domain import (
    CharacterCard,
    Choice,
    ChoiceDrivenStoryMeta,
    Message,
    SceneDescription,
    SceneMetadata,
    SceneRef,
    Step,
    StoryMeta,
)

# ---------------------------------------------------------------------------
# Domain object builders
# ---------------------------------------------------------------------------

_DEFAULT_STORY_ID = "story-1"
_DEFAULT_SCENE_ID = 1


def make_scene_metadata(
    finished: bool = False,
    context: list[str] | None = None,
    story_id: str = _DEFAULT_STORY_ID,
    scene_id: int = _DEFAULT_SCENE_ID,
) -> SceneMetadata:
    return SceneMetadata(
        id=scene_id,
        story_id=story_id,
        character_ids=["c1"],
        user_character_id="max",
        finished=finished,
        scene_description=SceneDescription(
            general_scene_guide="Guide text.",
            writing_style="Descriptive.",
        ),
        scene_summary=None,
        context=context,
    )


def make_messages(n: int = 2) -> list[Message]:
    return [
        Message(id=i + 1, role="user" if i % 2 == 0 else "assistant", content=f"Message {i + 1}")
        for i in range(n)
    ]


def make_story_meta(scenes: list[SceneRef], story_id: str = _DEFAULT_STORY_ID) -> StoryMeta:
    return StoryMeta(id=story_id, title="Test Story", scenes=scenes, active_scene_id=None)


def make_step(step_id: int, incoming_choice: Choice | None = None) -> Step:
    return Step(
        id=step_id,
        incoming_choice=incoming_choice,
        text=f"Paragraph {step_id}.",
        choices=[],
    )


# ---------------------------------------------------------------------------
# API mock-service builders (used in tests/api/)
# ---------------------------------------------------------------------------

_USER_MSG = Message(id=1, role="user", content="Hello")
_ASSISTANT_MSG = Message(id=2, role="assistant", content="Hi there!")


def make_play_service(
    play_side_effect: Exception | None = None,
    play_return: tuple | None = None,
    regen_side_effect: Exception | None = None,
    regen_return: Message | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc.play = (
        AsyncMock(side_effect=play_side_effect)
        if play_side_effect is not None
        else AsyncMock(return_value=play_return or (_USER_MSG, _ASSISTANT_MSG))
    )
    svc.regenerate = (
        AsyncMock(side_effect=regen_side_effect)
        if regen_side_effect is not None
        else AsyncMock(return_value=regen_return or _ASSISTANT_MSG)
    )
    return svc


def make_message_service(
    edit_side_effect: Exception | None = None,
    delete_side_effect: Exception | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc.edit_message = (
        AsyncMock(side_effect=edit_side_effect)
        if edit_side_effect is not None
        else AsyncMock(return_value=_USER_MSG)
    )
    svc.delete_message = (
        AsyncMock(side_effect=delete_side_effect)
        if delete_side_effect is not None
        else AsyncMock(return_value=None)
    )
    return svc


def make_lifecycle_service(finish_side_effect: Exception | None = None) -> MagicMock:
    svc = MagicMock()
    svc.finish_scene = (
        AsyncMock(side_effect=finish_side_effect)
        if finish_side_effect is not None
        else AsyncMock(return_value=None)
    )
    return svc


def make_summarize_service(
    side_effect: Exception | None = None,
    return_value: list[str] | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc.summarize = (
        AsyncMock(side_effect=side_effect)
        if side_effect is not None
        else AsyncMock(return_value=return_value or ["Item one", "Item two"])
    )
    return svc


def make_creation_service(
    side_effect: Exception | None = None,
    return_value: SceneRef | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc.create = (
        AsyncMock(side_effect=side_effect)
        if side_effect is not None
        else AsyncMock(return_value=return_value or SceneRef(id=3, finished=False))
    )
    return svc


_QUERY_SERVICE_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"

_QUERY_SERVICE_DEFAULT_METADATA = SceneMetadata(
    id=1,
    story_id=_QUERY_SERVICE_STORY_ID,
    character_ids=["villain"],
    user_character_id="hero",
    finished=False,
    scene_description=SceneDescription(
        general_scene_guide="Keep tension rising.",
        writing_style="Cinematic.",
    ),
    scene_summary=None,
    context=["Previously...", "And then..."],
)


def make_query_service(
    side_effect: Exception | None = None,
    metadata: SceneMetadata | None = None,
    messages: list[Message] | None = None,
) -> MagicMock:
    svc = MagicMock()
    if side_effect is not None:
        svc.get_scene = AsyncMock(side_effect=side_effect)
    else:
        svc.get_scene = AsyncMock(
            return_value=(
                metadata or _QUERY_SERVICE_DEFAULT_METADATA,
                messages or [_ASSISTANT_MSG],
            )
        )
    return svc


_DEFAULT_CHARACTERS = [
    CharacterCard(id="mila", name="Mila", features={}, memory=[]),
    CharacterCard(id="bun", name="Bun", features={}, memory=[]),
    CharacterCard(id="max", name="Max", features={}, memory=[]),
]


def make_character_repo(
    list_side_effect: Exception | None = None,
    list_return: list[CharacterCard] | None = None,
) -> MagicMock:
    repo = MagicMock()
    repo.list_characters = (
        AsyncMock(side_effect=list_side_effect)
        if list_side_effect is not None
        else AsyncMock(return_value=list_return or _DEFAULT_CHARACTERS)
    )
    return repo


_CD_CHOICE_A = Choice(action="Go left", consequence="Find a shortcut")
_CD_CHOICE_B = Choice(action="Go right", consequence="Meet a stranger")
_CD_STEP_1 = Step(id=1, incoming_choice=None, text="The fog rolled in.", choices=[_CD_CHOICE_A, _CD_CHOICE_B])
_CD_STEP_2 = Step(id=2, incoming_choice=_CD_CHOICE_A, text="A shortcut appeared.", choices=[])
_CD_META = ChoiceDrivenStoryMeta(
    id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
    title="The Black Harbor",
    writing_style="dark, suspenseful",
    plot_directions=["Romance", "Betrayal"],
    user_character_id="hero",
    character_ids=["c1"],
)
_CD_MISSING_ID = "00000000-0000-0000-0000-000000000000"


def make_choice_driven_service(
    steps: list[Step] | None = None,
    choices: list[Choice] | None = None,
    new_step: Step | None = None,
    edited_step: Step | None = None,
    returned_step_id: int = 1,
    story_not_found: bool = False,
    generate_choices_side_effect: Exception | None = None,
    regenerate_choices_side_effect: Exception | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc._repo = MagicMock()
    if story_not_found:
        err = NotFoundError(_CD_MISSING_ID)
        svc._repo.get_story_meta = AsyncMock(side_effect=err)
        svc.get_play_state = AsyncMock(side_effect=err)
        svc.generate_choices = AsyncMock(side_effect=err)
        svc.regenerate_choices = AsyncMock(side_effect=err)
        svc.select_choice = AsyncMock(side_effect=err)
        svc.edit_step_text = AsyncMock(side_effect=err)
        svc.return_to_step = AsyncMock(side_effect=err)
    else:
        svc._repo.get_story_meta = AsyncMock(return_value=_CD_META)
        svc.get_play_state = AsyncMock(return_value=steps or [_CD_STEP_1, _CD_STEP_2])
        svc.generate_choices = (
            AsyncMock(side_effect=generate_choices_side_effect)
            if generate_choices_side_effect is not None
            else AsyncMock(return_value=choices or [_CD_CHOICE_A, _CD_CHOICE_B])
        )
        svc.regenerate_choices = (
            AsyncMock(side_effect=regenerate_choices_side_effect)
            if regenerate_choices_side_effect is not None
            else AsyncMock(return_value=choices or [_CD_CHOICE_A, _CD_CHOICE_B])
        )
        svc.select_choice = AsyncMock(return_value=new_step or _CD_STEP_2)
        svc.edit_step_text = AsyncMock(return_value=edited_step or _CD_STEP_1)
        svc.return_to_step = AsyncMock(return_value=returned_step_id)
    return svc
