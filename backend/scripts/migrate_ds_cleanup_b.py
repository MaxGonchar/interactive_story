"""
DS-Cleanup Option B Migration Script
======================================
Strips the self-referential ``id`` field from every story.yaml, meta.yaml,
and characters/<id>.yaml file under a given data root.

Before (story.yaml):
    id: "8fa93a9e-..."
    title: "Mila and Bun"
    scenes: ...

After (story.yaml):
    title: "Mila and Bun"
    scenes: ...

The same transformation applies to scene meta.yaml and character YAML files.

Usage (from project root):
    backend/.venv/bin/python backend/scripts/migrate_ds_cleanup_b.py [--data-root PATH]

Options:
    --data-root PATH   Path to the data/stories directory (default: data/stories)
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


def _strip_id(path: Path, dry_run: bool) -> bool:
    """Remove the ``id`` key from *path* if present. Returns True if changed."""
    data = _load(path)
    if "id" not in data:
        return False
    del data["id"]
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

        # story.yaml
        story_file = story_dir / "story.yaml"
        if story_file.exists():
            if _strip_id(story_file, dry_run):
                print(f"{'[dry-run] ' if dry_run else ''}stripped id from {story_file}")
                changed += 1
            else:
                skipped += 1

        # scenes/<id>/meta.yaml
        scenes_dir = story_dir / "scenes"
        if scenes_dir.is_dir():
            for scene_dir in sorted(scenes_dir.iterdir()):
                meta_file = scene_dir / "meta.yaml"
                if meta_file.exists():
                    if _strip_id(meta_file, dry_run):
                        print(f"{'[dry-run] ' if dry_run else ''}stripped id from {meta_file}")
                        changed += 1
                    else:
                        skipped += 1

        # characters/<id>.yaml
        characters_dir = story_dir / "characters"
        if characters_dir.is_dir():
            for char_file in sorted(characters_dir.glob("*.yaml")):
                if _strip_id(char_file, dry_run):
                    print(f"{'[dry-run] ' if dry_run else ''}stripped id from {char_file}")
                    changed += 1
                else:
                    skipped += 1

    print(
        f"\nDone. {'Would change' if dry_run else 'Changed'}: {changed}, "
        f"already clean: {skipped}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Strip self-referential id fields from story/scene/character YAML files."
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
    migrate(stories_root, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
