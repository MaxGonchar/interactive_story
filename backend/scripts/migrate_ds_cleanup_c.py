"""
DS-Cleanup Option C Migration Script
======================================
Converts ``scenes`` in every ``story.yaml`` file from the old object format::

    scenes:
      - id: 1
        finished: true
      - id: 2
        finished: false

to a plain list of integer scene IDs::

    scenes:
      - 1
      - 2

The ``finished`` flag is now the exclusive responsibility of each scene's
``meta.yaml`` file and is no longer stored in ``story.yaml``.

Usage (from project root):
    backend/.venv/bin/python backend/scripts/migrate_ds_cleanup_c.py [--data-root PATH]

Options:
    --data-root PATH   Path to the data/stories directory (default: data/stories)
    --dry-run          Print what would change without writing files

The script is idempotent: if ``scenes`` already contains integers, the file is
left untouched.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _dump(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _convert_story(path: Path, dry_run: bool) -> bool:
    """Convert ``scenes`` from object list to int list. Returns True if changed."""
    data = _load(path)
    scenes = data.get("scenes")
    if not scenes:
        return False

    # Already in new format (list of ints)
    if all(isinstance(s, int) for s in scenes):
        return False

    # Convert: each element is a dict with at least an "id" key
    new_scenes = [s["id"] for s in scenes if isinstance(s, dict) and "id" in s]
    if new_scenes == scenes:
        return False

    data["scenes"] = new_scenes
    if not dry_run:
        _dump(path, data)
    return True


def migrate(stories_root: Path, dry_run: bool) -> None:
    if not stories_root.is_dir():
        print(f"ERROR: stories root not found: {stories_root}", file=sys.stderr)
        sys.exit(1)

    changed = 0
    skipped = 0

    for story_dir in sorted(stories_root.iterdir()):
        if not story_dir.is_dir():
            continue

        story_file = story_dir / "story.yaml"
        if story_file.exists():
            if _convert_story(story_file, dry_run):
                print(f"{'[dry-run] ' if dry_run else ''}converted scenes in {story_file}")
                changed += 1
            else:
                skipped += 1

    print(
        f"\nDone. {'Would change' if dry_run else 'Changed'}: {changed}, "
        f"already clean: {skipped}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert scenes in story.yaml from object list to integer list."
    )
    parser.add_argument(
        "--data-root",
        default="data/stories",
        help="Path to the data/stories directory (default: data/stories)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing files",
    )
    args = parser.parse_args()

    stories_root = Path(args.data_root)
    if not stories_root.is_absolute():
        stories_root = Path.cwd() / stories_root

    migrate(stories_root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
