# Task 026: YAML Fixture Files for One Story

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Create sample YAML fixture files for one story with one scene under `data/`. These files serve as the known-good test fixtures for all repository unit tests in M4.

## Scope

What IS included:
- `data/stories/index.yaml` — one story entry
- `data/stories/<story_id>/story.yaml` — story metadata with one active scene
- `data/stories/<story_id>/characters/<character_id>.yaml` — one character card
- `data/stories/<story_id>/scenes/<scene_id>/metadata.yaml` — scene metadata, `finished: false`
- `data/stories/<story_id>/scenes/<scene_id>/messages.yaml` — two messages (one user, one assistant)

What is NOT included (deferred):
- Multiple stories or scenes
- Finished-scene fixtures (can be added per-test by copying and mutating)
- Any Python code

## Deliverable

Five YAML files under `data/` following the schemas in `docks/dev/data_storage_structure.md`.

```
data/
  stories/
    index.yaml
    8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8/
      story.yaml
      characters/
        captain-mora.yaml
      scenes/
        1/
          metadata.yaml
          messages.yaml
```

## Acceptance Criteria

- [ ] `data/stories/index.yaml` contains exactly one story entry with a valid UUID id and title
- [ ] `data/stories/<story_id>/story.yaml` references the same id, lists one scene, and sets `active_scene_id: 1`
- [ ] `data/stories/<story_id>/characters/captain-mora.yaml` matches the character card schema (id, story_id, name, traits, etc.)
- [ ] `data/stories/<story_id>/scenes/1/metadata.yaml` has `finished: false`, references `captain-mora` in `character_ids`, and includes all three `scene_description` fields
- [ ] `data/stories/<story_id>/scenes/1/messages.yaml` contains at least two messages with sequential ids, valid roles, and non-empty content
- [ ] All id cross-references are consistent (story_id matches, character_id matches, scene id matches folder name)

## Test Notes

Load each file manually with `python -c "import yaml; print(yaml.safe_load(open('data/stories/index.yaml')))"` and verify output matches expected structure. These files will be consumed automatically by repository unit tests in task 035.

## Dependencies

none
