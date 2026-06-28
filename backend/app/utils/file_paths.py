import os
from pathlib import Path


# This file lives at backend/app/utils/file_paths.py
# parents: [0]=utils  [1]=app  [2]=backend  [3]=repo_root
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[3] / "data-test"

_STORIES_DIR = "stories"
_CHARACTERS_DIR = "characters"
_SCENES_DIR = "scenes"

_INDEX_FILE = "index.yaml"
_STORY_FILE = "story.yaml"
_METADATA_FILE = "meta.yaml"
_MESSAGES_FILE = "messages.yaml"
_HISTORY_FILE = "history.yaml"


def _data_root() -> Path:
    raw = os.environ.get("DATA_ROOT")
    if raw is None:
        return _DEFAULT_DATA_ROOT
    p = Path(raw)
    if p.is_absolute():
        return p
    # Relative paths in DATA_ROOT are resolved from backend/
    return (_BACKEND_DIR / p).resolve()


def stories_index() -> Path:
    return _data_root() / _STORIES_DIR / _INDEX_FILE


def story_file(story_id: str) -> Path:
    return _data_root() / _STORIES_DIR / story_id / _STORY_FILE


def character_file(story_id: str, character_id: str) -> Path:
    return _data_root() / _STORIES_DIR / story_id / _CHARACTERS_DIR / f"{character_id}.yaml"


def scene_metadata_file(story_id: str, scene_id: int) -> Path:
    return _data_root() / _STORIES_DIR / story_id / _SCENES_DIR / str(scene_id) / _METADATA_FILE


def scene_messages_file(story_id: str, scene_id: int) -> Path:
    return _data_root() / _STORIES_DIR / story_id / _SCENES_DIR / str(scene_id) / _MESSAGES_FILE


def history_file(story_id: str) -> Path:
    return _data_root() / _STORIES_DIR / story_id / _HISTORY_FILE
