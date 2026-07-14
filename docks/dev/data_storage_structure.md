# Data Storage Structure (MVP)

## Scope
This document defines storage for MVP only.

In MVP:
- story and scene base content is prepared manually
- app reads/writes scene messages and scene finished status during play
- each story has its own character set (stored as separate character files)
- each scene defines its own character set (independent of story-level character lists)
- each scene has scene description metadata
- each finished scene has summary text
- messages in the active scene can be edited and deleted

Out of MVP:
- automated between-scene updates
- in-app creation of new stories/scenes
- in-app management of character and scene-description content

## Storage Technology
- Local disk storage
- YAML files
- Single-user local usage model

## Root Layout

```text
data/
  stories/
    <story_id>/
      story.yaml
      characters/
        <character_id>.yaml
      scenes/
        <scene_id>/
          meta.yaml
          messages.yaml
```

## File Responsibilities
- data/stories/<story_id>/story.yaml:
  - story-level metadata
  - ordered scene ids for story page
  - active scene pointer
- data/stories/<story_id>/characters/<character_id>.yaml:
  - full character card for a story character
- data/stories/<story_id>/scenes/<scene_id>/meta.yaml:
  - scene metadata (finished status, character set, user character, scene description, summary)
- data/stories/<story_id>/scenes/<scene_id>/messages.yaml:
  - scene message history only

## ID Rules
- story_id: UUID string — derived from the folder name `data/stories/<story_id>/`
- scene_id: integer, unique only within a story — derived from the folder name `scenes/<scene_id>/`
- character_id: kebab-case string, unique only within a story — derived from the filename `characters/<character_id>.yaml`
- message_id: integer, unique only within a scene

ID generation rules:
- new assistant message id = max(existing ids) + 1
- if no messages exist, first message id = 1
- message ids are never re-numbered after edit or delete operations

## YAML Schemas

### 1) Story Metadata
Path: data/stories/<story_id>/story.yaml

> The story ID is derived from the enclosing folder name, not stored inside the file.
> Scene IDs are derived from subfolder names under `scenes/`, not stored in this file.

```yaml
title: "The Black Harbor"
type: "scene"
created_at: "2024-06-01T12:00:00Z"
```

Constraints:
- `type` is required; valid values: `"scene"` | `"choice_driven"`
- `created_at` is required; ISO 8601 string
- stories are discovered by scanning `data/stories/` for subdirectories; IDs are derived from folder names
- stories are sorted by `created_at` desc when returned from list
- scene IDs are discovered by listing `scenes/<scene_id>/` subfolder names (integer, sorted ascending)
- the `finished` state for each scene is stored exclusively in that scene's `meta.yaml`

### 3) Character Card
Path: data/stories/<story_id>/characters/<character_id>.yaml

> The character ID is derived from the filename, not stored inside the file.

```yaml
name: "Captain Mora"
appearance: "Tall, sea-worn coat, scar over left eyebrow"
traits:
  - "pragmatic"
  - "suspicious"
speech_patterns:
  - "short direct phrases"
body_language:
  - "folded arms"
  - "controlled pacing"
likes:
  - "clear orders"
fears:
  - "mutiny"
memory:
  - "Lost her first crew in a storm"
```

Constraints:
- name must be non-empty string

### 4) Scene Metadata
Path: data/stories/<story_id>/scenes/<scene_id>/meta.yaml

> The scene ID is derived from the enclosing folder name, not stored inside the file.

```yaml
finished: false
character_ids:
  - "captain-mora"
user_character_id: "player"
scene_description:
  general_scene_guide: "Keep tension rising with small discoveries and choices."
  writing_style: "Cinematic, sensory details, concise dialog turns."
scene_summary: null
context:
  - "You arrived at the harbor and met Captain Mora, who warned you of dangers ahead."
  - "You decided to explore the docks for supplies before setting out to sea."
```

Constraints:
- finished is boolean
- each character_id must have a matching character file in characters/<character_id>.yaml
- user_character_id must have a matching character file in characters/<user_character_id>.yaml
- scene_description must include: general_scene_guide, writing_style
  
### 5) Scene Messages
Path: data/stories/<story_id>/scenes/<scene_id>/messages.yaml

```yaml
messages:
  - id: 1
    role: "assistant"
    content: "You step into the foggy harbor..."
  - id: 2
    role: "user"
    content: "I look for the nearest light source."
  - id: 3
    role: "assistant"
    content: "A lantern swings near a wooden post..."
```

Constraints:
- messages are strictly ordered by id asc
- role must be one of: user, assistant
- content must be non-empty string

## Repository Invariants
- A scene with finished=true cannot accept new user message through play operation.
- Message edits and deletions are allowed only while scene is not finished.
- Message ids are stable and are never re-numbered after edit or delete operations.
- Every successful play operation appends one user message and one assistant message.
- On LLM failure, user message append behavior must follow API contract decision (to be finalized in endpoints doc).

## Atomic Write Strategy
All writes must be atomic per file.

Write algorithm:
1. Serialize YAML to bytes.
2. Write to temp file in same directory: <target>.tmp
3. Flush and fsync temp file.
4. Rename temp file to target file (atomic replace).
5. Optionally fsync directory metadata.

Why same directory:
- rename is atomic only within same filesystem boundary.

## Concurrency Model (MVP)
- Single-process app, local user.
- Use per-scene in-process lock for scene write operations.
- Lock key: story_id + scene_id.

## Read/Write Mapping to MVP Operations
- list stories:
  - scan data/stories/ for story subdirectories
  - read each story.yaml concurrently
  - sort by created_at desc
- get story and scenes list:
  - read story.yaml
  - read each scene meta.yaml for finished status
- open last scene:
  - read story.yaml -> active_scene_id
  - read scene meta.yaml
  - read scene messages.yaml
- play scene:
  - read scene meta.yaml
  - validate not finished
  - read scene messages.yaml
  - append user + assistant messages
  - atomic write messages.yaml
- edit message:
  - read scene meta.yaml
  - validate not finished
  - read scene messages.yaml
  - update target message content in place
  - atomic write messages.yaml
- delete message:
  - read scene meta.yaml
  - validate not finished
  - read scene messages.yaml
  - remove target message without re-numbering remaining ids
  - atomic write messages.yaml
- finish scene:
  - read scene meta.yaml
  - set finished=true
  - persist scene_summary
  - atomic write meta.yaml

## Validation Rules at Repository Boundary
- reject malformed YAML as repository error
- reject missing referenced files as not-found errors
- reject schema-invalid documents as data integrity errors

## Manual Content Update Policy (MVP)
- stories/scenes base content is created and modified manually outside app flows
- manual edits must preserve schema and id invariants above
