from __future__ import annotations

import pytest
import yaml

from app.models.domain import Choice, ChoiceDrivenStoryMeta, Step
from app.repositories.choice_driven_story_repository import ChoiceDrivenStoryRepository

STORY_ID = "cds-test-story"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def story_root(monkeypatch, tmp_path):
    """Set DATA_ROOT to tmp_path and seed a minimal choice-driven story.yaml."""
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    story_dir = tmp_path / "stories" / STORY_ID
    story_dir.mkdir(parents=True)

    story_data = {
        "id": STORY_ID,
        "title": "Fog City",
        "type": "choice_driven",
        "character_ids": ["john"],
        "writing_style": "Dark and suspenseful",
        "plot_directions": ["Romance", "Betrayal"],
    }
    (story_dir / "story.yaml").write_text(
        yaml.safe_dump(story_data, allow_unicode=True), encoding="utf-8"
    )
    return tmp_path


def _make_step(step_id: int, incoming_choice: Choice | None = None) -> Step:
    return Step(
        id=step_id,
        incoming_choice=incoming_choice,
        text=f"Paragraph {step_id}.",
        choices=[],
    )


# ---------------------------------------------------------------------------
# get_story_meta
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_story_meta_returns_correct_data(story_root):
    repo = ChoiceDrivenStoryRepository()
    meta = await repo.get_story_meta(STORY_ID)

    assert isinstance(meta, ChoiceDrivenStoryMeta)
    assert meta.id == STORY_ID
    assert meta.title == "Fog City"
    assert meta.writing_style == "Dark and suspenseful"
    assert meta.plot_directions == ["Romance", "Betrayal"]
    assert meta.character_ids == ["john"]


@pytest.mark.asyncio
async def test_get_story_meta_missing_story_raises_key_error(story_root):
    repo = ChoiceDrivenStoryRepository()

    with pytest.raises(KeyError):
        await repo.get_story_meta("nonexistent-story")


# ---------------------------------------------------------------------------
# get_history — missing file returns []
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_history_returns_empty_list_when_file_missing(story_root):
    repo = ChoiceDrivenStoryRepository()
    result = await repo.get_history(STORY_ID)

    assert result == []


# ---------------------------------------------------------------------------
# append_step / get_history round-trip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_append_step_then_get_history_round_trip(story_root):
    repo = ChoiceDrivenStoryRepository()
    step = _make_step(1)

    await repo.append_step(STORY_ID, step)
    history = await repo.get_history(STORY_ID)

    assert len(history) == 1
    assert isinstance(history[0], Step)
    assert history[0].id == 1
    assert history[0].text == "Paragraph 1."
    assert history[0].incoming_choice is None


@pytest.mark.asyncio
async def test_append_multiple_steps_preserves_order(story_root):
    repo = ChoiceDrivenStoryRepository()
    choice = Choice(action="Enter fog", consequence="Figure appears")

    await repo.append_step(STORY_ID, _make_step(1))
    await repo.append_step(STORY_ID, _make_step(2, incoming_choice=choice))
    await repo.append_step(STORY_ID, _make_step(3, incoming_choice=choice))

    history = await repo.get_history(STORY_ID)

    assert [s.id for s in history] == [1, 2, 3]
    assert history[1].incoming_choice.action == "Enter fog"


# ---------------------------------------------------------------------------
# update_step_choices
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_step_choices_replaces_choices(story_root):
    repo = ChoiceDrivenStoryRepository()
    await repo.append_step(STORY_ID, _make_step(1))

    new_choices = [
        Choice(action="A", consequence="Outcome A"),
        Choice(action="B", consequence="Outcome B"),
    ]
    await repo.update_step_choices(STORY_ID, step_id=1, choices=new_choices)
    history = await repo.get_history(STORY_ID)

    assert len(history[0].choices) == 2
    assert history[0].choices[0].action == "A"
    assert history[0].choices[1].action == "B"


@pytest.mark.asyncio
async def test_update_step_choices_nonexistent_step_raises_key_error(story_root):
    repo = ChoiceDrivenStoryRepository()
    await repo.append_step(STORY_ID, _make_step(1))

    with pytest.raises(KeyError):
        await repo.update_step_choices(STORY_ID, step_id=99, choices=[])


# ---------------------------------------------------------------------------
# update_step_text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_step_text_changes_text(story_root):
    repo = ChoiceDrivenStoryRepository()
    await repo.append_step(STORY_ID, _make_step(1))

    await repo.update_step_text(STORY_ID, step_id=1, text="Corrected paragraph.")
    history = await repo.get_history(STORY_ID)

    assert history[0].text == "Corrected paragraph."


@pytest.mark.asyncio
async def test_update_step_text_nonexistent_step_raises_key_error(story_root):
    repo = ChoiceDrivenStoryRepository()
    await repo.append_step(STORY_ID, _make_step(1))

    with pytest.raises(KeyError):
        await repo.update_step_text(STORY_ID, step_id=99, text="New text.")


# ---------------------------------------------------------------------------
# truncate_from
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_truncate_from_removes_steps_after_given_id(story_root):
    repo = ChoiceDrivenStoryRepository()
    choice = Choice(action="Go", consequence="Arrive")

    for i in range(1, 5):
        await repo.append_step(STORY_ID, _make_step(i, None if i == 1 else choice))

    await repo.truncate_from(STORY_ID, step_id=2)
    history = await repo.get_history(STORY_ID)

    assert [s.id for s in history] == [1, 2]


@pytest.mark.asyncio
async def test_truncate_from_keeps_all_when_step_id_is_last(story_root):
    repo = ChoiceDrivenStoryRepository()

    for i in range(1, 4):
        await repo.append_step(STORY_ID, _make_step(i))

    await repo.truncate_from(STORY_ID, step_id=3)
    history = await repo.get_history(STORY_ID)

    assert len(history) == 3


@pytest.mark.asyncio
async def test_truncate_from_removes_all_when_step_id_is_zero(story_root):
    repo = ChoiceDrivenStoryRepository()

    for i in range(1, 4):
        await repo.append_step(STORY_ID, _make_step(i))

    await repo.truncate_from(STORY_ID, step_id=0)
    history = await repo.get_history(STORY_ID)

    assert history == []


# ---------------------------------------------------------------------------
# Atomic write — file is valid YAML after each operation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_file_is_valid_yaml_after_append(story_root):
    repo = ChoiceDrivenStoryRepository()
    await repo.append_step(STORY_ID, _make_step(1))

    from app.utils.file_paths import history_file

    raw = history_file(STORY_ID).read_text(encoding="utf-8")
    parsed = yaml.safe_load(raw)
    assert "steps" in parsed
    assert parsed["steps"][0]["id"] == 1
