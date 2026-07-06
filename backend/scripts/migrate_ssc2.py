"""
SSC-2 Data Migration Script
============================
Migrates production `data/` YAML files from the old schema (SSC-1 era) to the
new schema introduced in SSC-1 code changes:

Old story.yaml schema:
    id, title, user_character_id, character_ids, scenes

New story.yaml schema (fields removed):
    id, title, scenes

Old scene meta.yaml schema:
    characters_ids, finished, id, scene_description, scene_summary, story_id, context

New scene meta.yaml schema (field renamed + new field added):
    character_ids, user_character_id, finished, id, scene_description, scene_summary, story_id, context

Usage (from project root):
    backend/.venv/bin/python backend/scripts/migrate_ssc2.py [--data-root PATH]

Options:
    --data-root PATH   Path to the data directory (default: data/)
    --dry-run          Print what would change without writing files

The script is idempotent: running it multiple times produces the same result.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml


def _load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _dump(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def migrate_story(story_path: Path, dry_run: bool) -> tuple[bool, str]:
    """
    Remove `user_character_id` and `character_ids` from story.yaml.
    Returns (changed, user_character_id_value).
    user_character_id_value is read before removal so callers can propagate it.
    """
    data = _load(story_path)

    user_character_id = data.get("user_character_id")
    character_ids = data.get("character_ids")

    needs_change = "user_character_id" in data or "character_ids" in data

    if needs_change:
        data.pop("user_character_id", None)
        data.pop("character_ids", None)
        if not dry_run:
            _dump(story_path, data)

    return needs_change, user_character_id, character_ids


def migrate_scene_meta(
    meta_path: Path,
    user_character_id: str | None,
    dry_run: bool,
) -> bool:
    """
    Rename `characters_ids` → `character_ids` and add `user_character_id`.
    Idempotent: if already migrated, returns False (no change).
    """
    data = _load(meta_path)

    changed = False

    # Rename characters_ids → character_ids
    if "characters_ids" in data and "character_ids" not in data:
        data["character_ids"] = data.pop("characters_ids")
        changed = True
    elif "characters_ids" in data and "character_ids" in data:
        # Both present — remove the old key
        data.pop("characters_ids")
        changed = True

    # Add user_character_id if missing
    if "user_character_id" not in data:
        if user_character_id is None:
            print(
                f"  WARNING: no user_character_id available for {meta_path} — skipping field",
                file=sys.stderr,
            )
        else:
            data["user_character_id"] = user_character_id
            changed = True

    if changed and not dry_run:
        _dump(meta_path, data)

    return changed


def migrate(data_root: Path, dry_run: bool) -> None:
    stories_dir = data_root / "stories"
    if not stories_dir.exists():
        print(f"No stories directory found at {stories_dir}", file=sys.stderr)
        sys.exit(1)

    total_stories = 0
    total_scenes = 0
    changed_stories = 0
    changed_scenes = 0

    for story_dir in sorted(stories_dir.iterdir()):
        if not story_dir.is_dir():
            continue

        story_yaml = story_dir / "story.yaml"
        if not story_yaml.exists():
            continue

        total_stories += 1
        story_changed, user_character_id, character_ids = migrate_story(story_yaml, dry_run)

        action = "updated" if story_changed else "skipped (already migrated)"
        if dry_run and story_changed:
            action = "would update"
        print(f"story.yaml  [{action}]: {story_yaml}")

        if story_changed:
            changed_stories += 1

        scenes_dir = story_dir / "scenes"
        if not scenes_dir.exists():
            continue

        for scene_dir in sorted(scenes_dir.iterdir()):
            if not scene_dir.is_dir():
                continue

            meta_yaml = scene_dir / "meta.yaml"
            if not meta_yaml.exists():
                continue

            total_scenes += 1
            scene_changed = migrate_scene_meta(meta_yaml, user_character_id, dry_run)

            action = "updated" if scene_changed else "skipped (already migrated)"
            if dry_run and scene_changed:
                action = "would update"
            print(f"meta.yaml   [{action}]: {meta_yaml}")

            if scene_changed:
                changed_scenes += 1

    prefix = "[DRY RUN] " if dry_run else ""
    print(
        f"\n{prefix}Done. "
        f"Stories: {changed_stories}/{total_stories} updated. "
        f"Scenes: {changed_scenes}/{total_scenes} updated."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate data/ YAML files to the SSC-2 schema."
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
