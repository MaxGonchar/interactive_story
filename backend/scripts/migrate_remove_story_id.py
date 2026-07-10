"""
DS-Cleanup Migration Script
============================
Removes the stale `story_id` field from character YAML files and scene
metadata YAML files.

These files may contain a top-level `story_id` key that was written by an
older version of the application. The field is now derived exclusively from
the file-system path and is no longer read or written by the application.

Affected file types:
    data/stories/<story_id>/characters/<character_id>.yaml
    data/stories/<story_id>/scenes/<scene_id>/meta.yaml

Usage (from project root):
    backend/.venv/bin/python backend/scripts/migrate_remove_story_id.py [--data-root PATH]

Options:
    --data-root PATH   Path to the data directory (default: data/)
    --dry-run          Print what would change without writing files

The script is idempotent: running it multiple times produces the same result.
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


def migrate_file(path: Path, dry_run: bool) -> bool:
    """Remove `story_id` from *path* if present. Returns True if changed."""
    data = _load(path)

    if "story_id" not in data:
        return False

    data.pop("story_id")
    if not dry_run:
        _dump(path, data)

    return True


def migrate(data_root: Path, dry_run: bool) -> None:
    stories_dir = data_root / "stories"
    if not stories_dir.exists():
        print(f"No stories directory found at {stories_dir}", file=sys.stderr)
        sys.exit(1)

    total = 0
    changed = 0

    for story_dir in sorted(stories_dir.iterdir()):
        if not story_dir.is_dir():
            continue

        # Character files
        characters_dir = story_dir / "characters"
        if characters_dir.exists():
            for char_file in sorted(characters_dir.glob("*.yaml")):
                total += 1
                was_changed = migrate_file(char_file, dry_run)
                action = _action_label(was_changed, dry_run)
                print(f"character   [{action}]: {char_file}")
                if was_changed:
                    changed += 1

        # Scene metadata files
        scenes_dir = story_dir / "scenes"
        if scenes_dir.exists():
            for scene_dir in sorted(scenes_dir.iterdir()):
                if not scene_dir.is_dir():
                    continue
                meta_yaml = scene_dir / "meta.yaml"
                if not meta_yaml.exists():
                    continue
                total += 1
                was_changed = migrate_file(meta_yaml, dry_run)
                action = _action_label(was_changed, dry_run)
                print(f"meta.yaml   [{action}]: {meta_yaml}")
                if was_changed:
                    changed += 1

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Done. {changed}/{total} files updated.")


def _action_label(changed: bool, dry_run: bool) -> str:
    if not changed:
        return "skipped (already migrated)"
    return "would update" if dry_run else "updated"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove stale story_id fields from character and scene metadata YAML files."
    )
    parser.add_argument(
        "--data-root",
        default="data",
        help="Path to the data directory (default: data/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing files",
    )
    args = parser.parse_args()

    data_root = Path(args.data_root)
    if not data_root.exists():
        print(f"Error: data root '{data_root}' does not exist.", file=sys.stderr)
        sys.exit(1)

    migrate(data_root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
