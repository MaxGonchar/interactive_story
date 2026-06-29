from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import NoStepsError
from app.models.domain import Choice, ChoiceDrivenStoryMeta, Step
from app.services.choice_driven_play_service import ChoiceDrivenPlayService

_STORY_ID = "story-1"

_CHOICE_A = Choice(action="Act A", consequence="Con A")
_CHOICE_B = Choice(action="Act B", consequence="Con B")
_CHOICE_C = Choice(action="Act C", consequence="Con C")
_CHOICE_D = Choice(action="Act D", consequence="Con D")

_META = ChoiceDrivenStoryMeta(
    id=_STORY_ID,
    title="Test Story",
    writing_style="terse",
    plot_directions=["direction-1", "direction-2"],
    character_ids=["c1", "c2"],
)


def _make_steps(n: int = 3) -> list[Step]:
    return [
        Step(id=i + 1, incoming_choice=None, text=f"Paragraph {i + 1}.", choices=[])
        for i in range(n)
    ]


def _make_service(
    meta: ChoiceDrivenStoryMeta = _META,
    steps: list[Step] | None = None,
) -> tuple[ChoiceDrivenPlayService, MagicMock, MagicMock]:
    if steps is None:
        steps = _make_steps()

    repo = MagicMock()
    repo.get_story_meta = AsyncMock(return_value=meta)
    repo.get_history = AsyncMock(return_value=steps)
    repo.append_step = AsyncMock()
    repo.update_step_choices = AsyncMock()
    repo.update_step_text = AsyncMock()
    repo.truncate_from = AsyncMock()

    character_repo = MagicMock()
    character_repo.get_characters = AsyncMock(return_value=[])

    service = ChoiceDrivenPlayService(repo=repo, character_repo=character_repo)
    return service, repo, character_repo


# ---------------------------------------------------------------------------
# get_play_state
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_play_state_returns_history():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    result = await service.get_play_state(_STORY_ID)

    repo.get_history.assert_awaited_once_with(_STORY_ID)
    assert result == steps


# ---------------------------------------------------------------------------
# generate_choices
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_choices_creates_one_client_per_direction():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    mock_client = MagicMock()
    mock_client.invoke = AsyncMock(return_value=[_CHOICE_A, _CHOICE_B])

    with patch(
        "app.services.choice_driven_play_service.ChoiceEngineClient",
        return_value=mock_client,
    ) as MockClass:
        result = await service.generate_choices(_STORY_ID)

    # One instantiation per plot direction
    assert MockClass.call_count == len(_META.plot_directions)
    # invoke called on each instance
    assert mock_client.invoke.await_count == len(_META.plot_directions)
    # results are flattened: 2 directions × 2 choices = 4
    assert len(result) == 4


@pytest.mark.asyncio
async def test_generate_choices_persists_to_latest_step():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    mock_client = MagicMock()
    mock_client.invoke = AsyncMock(return_value=[_CHOICE_A])

    with patch(
        "app.services.choice_driven_play_service.ChoiceEngineClient",
        return_value=mock_client,
    ):
        choices = await service.generate_choices(_STORY_ID)

    repo.update_step_choices.assert_awaited_once_with(_STORY_ID, steps[-1].id, choices)


@pytest.mark.asyncio
async def test_generate_choices_passes_full_story_text():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    captured_texts: list[str] = []
    mock_client = MagicMock()

    async def capture_invoke(text: str) -> list[Choice]:
        captured_texts.append(text)
        return [_CHOICE_A]

    mock_client.invoke = capture_invoke

    with patch(
        "app.services.choice_driven_play_service.ChoiceEngineClient",
        return_value=mock_client,
    ):
        await service.generate_choices(_STORY_ID)

    expected = "\n\n".join(s.text for s in steps)
    assert all(t == expected for t in captured_texts)


@pytest.mark.asyncio
async def test_generate_choices_raises_when_no_steps():
    service, _, _ = _make_service(steps=[])

    with pytest.raises(NoStepsError):
        await service.generate_choices(_STORY_ID)


# ---------------------------------------------------------------------------
# regenerate_choices
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_regenerate_choices_clears_then_generates():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    mock_client = MagicMock()
    mock_client.invoke = AsyncMock(return_value=[_CHOICE_A])

    call_order: list[str] = []

    async def track_clear(story_id: str, step_id: int, choices: list) -> None:
        call_order.append("clear")

    async def track_generate(text: str) -> list[Choice]:
        call_order.append("generate")
        return [_CHOICE_A]

    repo.update_step_choices.side_effect = track_clear
    mock_client.invoke = track_generate

    with patch(
        "app.services.choice_driven_play_service.ChoiceEngineClient",
        return_value=mock_client,
    ):
        await service.regenerate_choices(_STORY_ID)

    # clear must happen before generate
    assert call_order[0] == "clear"
    assert "generate" in call_order
    # First call clears existing choices
    first_call = repo.update_step_choices.call_args_list[0]
    assert first_call.args == (_STORY_ID, steps[-1].id, [])


@pytest.mark.asyncio
async def test_regenerate_choices_raises_when_no_steps():
    service, _, _ = _make_service(steps=[])

    with pytest.raises(NoStepsError):
        await service.regenerate_choices(_STORY_ID)


# ---------------------------------------------------------------------------
# select_choice
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_select_choice_appends_new_step():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    mock_engine = MagicMock()
    mock_engine.invoke = AsyncMock(return_value="New paragraph text.")

    with patch(
        "app.services.choice_driven_play_service.StoryEngineClient",
        return_value=mock_engine,
    ):
        result = await service.select_choice(_STORY_ID, _CHOICE_A)

    repo.append_step.assert_awaited_once()
    appended: Step = repo.append_step.call_args.args[1]
    assert appended.id == steps[-1].id + 1
    assert appended.incoming_choice == _CHOICE_A
    assert appended.text == "New paragraph text."
    assert appended.choices == []
    assert result == appended


@pytest.mark.asyncio
async def test_select_choice_passes_action_and_consequence():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    mock_engine = MagicMock()
    mock_engine.invoke = AsyncMock(return_value="reply")

    with patch(
        "app.services.choice_driven_play_service.StoryEngineClient",
        return_value=mock_engine,
    ):
        await service.select_choice(_STORY_ID, _CHOICE_A)

    mock_engine.invoke.assert_awaited_once()
    _, action_arg, consequence_arg = mock_engine.invoke.call_args.args
    assert action_arg == _CHOICE_A.action
    assert consequence_arg == _CHOICE_A.consequence


@pytest.mark.asyncio
async def test_select_choice_uses_last_10_paragraphs():
    # 12 steps — only the last 10 should be passed to StoryEngineClient
    steps = _make_steps(12)
    service, repo, _ = _make_service(steps=steps)

    captured_story_text: list[str] = []
    mock_engine = MagicMock()

    async def capture(story_text: str, action: str, consequence: str) -> str:
        captured_story_text.append(story_text)
        return "reply"

    mock_engine.invoke = capture

    with patch(
        "app.services.choice_driven_play_service.StoryEngineClient",
        return_value=mock_engine,
    ):
        await service.select_choice(_STORY_ID, _CHOICE_A)

    expected = "\n\n".join(s.text for s in steps[-10:])
    assert captured_story_text[0] == expected


@pytest.mark.asyncio
async def test_select_choice_window_not_exceeded_when_fewer_than_10_steps():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    captured_story_text: list[str] = []
    mock_engine = MagicMock()

    async def capture(story_text: str, action: str, consequence: str) -> str:
        captured_story_text.append(story_text)
        return "reply"

    mock_engine.invoke = capture

    with patch(
        "app.services.choice_driven_play_service.StoryEngineClient",
        return_value=mock_engine,
    ):
        await service.select_choice(_STORY_ID, _CHOICE_A)

    expected = "\n\n".join(s.text for s in steps)
    assert captured_story_text[0] == expected


# ---------------------------------------------------------------------------
# edit_step_text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_edit_step_text_delegates_and_returns_updated_step():
    steps = _make_steps(3)
    target = steps[1]
    service, repo, _ = _make_service(steps=steps)

    result = await service.edit_step_text(_STORY_ID, target.id, "Updated text.")

    repo.update_step_text.assert_awaited_once_with(_STORY_ID, target.id, "Updated text.")
    assert result.id == target.id


# ---------------------------------------------------------------------------
# return_to_step
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_return_to_step_delegates_truncate_and_returns_step_id():
    steps = _make_steps(3)
    service, repo, _ = _make_service(steps=steps)

    result = await service.return_to_step(_STORY_ID, step_id=2)

    repo.truncate_from.assert_awaited_once_with(_STORY_ID, 2)
    assert result == 2
