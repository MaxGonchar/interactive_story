import os

import pytest

import app.utils.file_paths as fp


@pytest.fixture()
def fixed_root(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    yield tmp_path


def test_stories_index(fixed_root):
    result = fp.stories_index()
    assert str(result) == str(fixed_root / "stories" / "index.yaml")


def test_story_file(fixed_root):
    result = fp.story_file("abc")
    assert str(result) == str(fixed_root / "stories" / "abc" / "story.yaml")


def test_character_file(fixed_root):
    result = fp.character_file("abc", "captain-mora")
    assert str(result) == str(fixed_root / "stories" / "abc" / "characters" / "captain-mora.yaml")


def test_scene_metadata_file(fixed_root):
    result = fp.scene_metadata_file("abc", 1)
    assert str(result) == str(fixed_root / "stories" / "abc" / "scenes" / "1" / "meta.yaml")


def test_scene_messages_file(fixed_root):
    result = fp.scene_messages_file("abc", 1)
    assert str(result) == str(fixed_root / "stories" / "abc" / "scenes" / "1" / "messages.yaml")


def test_all_functions_return_path_objects(fixed_root):
    from pathlib import Path
    assert isinstance(fp.stories_index(), Path)
    assert isinstance(fp.story_file("x"), Path)
    assert isinstance(fp.character_file("x", "y"), Path)
    assert isinstance(fp.scene_metadata_file("x", 1), Path)
    assert isinstance(fp.scene_messages_file("x", 1), Path)


def test_data_root_default_is_data_folder(monkeypatch):
    monkeypatch.delenv("DATA_ROOT", raising=False)
    assert fp._data_root().name == "data-test"
