# Data Storage Structure (MVP)

## Scope
This document defines storage for MVP only.

In MVP:
- story and scene base content is prepared manually
- app reads/writes scene messages and scene finished status during play
- each story has its own character set (stored as separate character files)
- each scene has its own subset of story characters
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
    index.yaml
    <story_id>/
      story.yaml
      characters/
        <character_id>.yaml
      scenes/
        <scene_id>/
          metadata.yaml
          messages.yaml
```

## File Responsibilities
- data/stories/index.yaml:
  - lightweight list for stories index page
  - source for ordered story listing
- data/stories/<story_id>/story.yaml:
  - story-level metadata
  - ordered scene ids for story page
  - active scene pointer
- data/stories/<story_id>/characters/<character_id>.yaml:
  - full character card for a story character
- data/stories/<story_id>/scenes/<scene_id>/metadata.yaml:
  - scene metadata (finished status, character subset, scene description, summary)
- data/stories/<story_id>/scenes/<scene_id>/messages.yaml:
  - scene message history only

## ID Rules
- story_id: UUID string
- scene_id: integer, unique only within a story
- character_id: kebab-case string, unique only within a story
- message_id: integer, unique only within a scene

ID generation rules:
- new assistant message id = max(existing ids) + 1
- if no messages exist, first message id = 1
- message ids are never re-numbered after edit or delete operations

## YAML Schemas

### 1) Stories Index
Path: data/stories/index.yaml

```yaml
stories:
  - id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
    title: "The Black Harbor"
    order: 1
```

Constraints:
- stories must be sorted by order asc when returned
- id must exist as folder data/stories/<id>/

### 2) Story Metadata
Path: data/stories/<story_id>/story.yaml

```yaml
id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
title: "The Black Harbor"
character_ids:
  - "captain-mora"
  - "dockmaster-elin"
scenes:
  - id: 1
    order: 1
  - id: 2
    order: 2
  - id: 3
    order: 3
active_scene_id: 3
```

Constraints:
- id must equal folder name <story_id>
- each character_id must have matching file in characters/<character_id>.yaml
- scenes must be sorted by order asc
- active_scene_id must refer to an existing scene id

### 3) Character Card
Path: data/stories/<story_id>/characters/<character_id>.yaml

```yaml
id: "captain-mora"
story_id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
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
- id must equal filename <character_id>.yaml
- story_id must equal parent folder story id
- name must be non-empty string

### 4) Scene Metadata
Path: data/stories/<story_id>/scenes/<scene_id>/metadata.yaml

```yaml
id: 3
story_id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
finished: false
character_ids:
  - "captain-mora"
scene_description:
  entry_point: "Fog rolls over the black harbor as bells ring in distance."
  general_scene_guide: "Keep tension rising with small discoveries and choices."
  writing_style: "Cinematic, sensory details, concise dialog turns."
scene_summary: null
```

Constraints:
- id must equal parent folder name <scene_id>
- story_id must equal parent folder story id
- finished is boolean
- each character_id must exist in story character_ids and have character file
- scene_description must include: entry_point, general_scene_guide, writing_style
- if finished=true, scene_summary must be non-empty string
- if finished=false, scene_summary may be null

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
- Scene character_ids must always be a subset of story character_ids.
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
  - read data/stories/index.yaml
- get story and scenes list:
  - read story.yaml
  - read each scene metadata.yaml for finished status
- open last scene:
  - read story.yaml -> active_scene_id
  - read scene metadata.yaml
  - read scene messages.yaml
- play scene:
  - read scene metadata.yaml
  - validate not finished
  - read scene messages.yaml
  - append user + assistant messages
  - atomic write messages.yaml
- edit message:
  - read scene metadata.yaml
  - validate not finished
  - read scene messages.yaml
  - update target message content in place
  - atomic write messages.yaml
- delete message:
  - read scene metadata.yaml
  - validate not finished
  - read scene messages.yaml
  - remove target message without re-numbering remaining ids
  - atomic write messages.yaml
- finish scene:
  - read scene metadata.yaml
  - set finished=true
  - persist scene_summary
  - atomic write metadata.yaml

## Validation Rules at Repository Boundary
- reject malformed YAML as repository error
- reject missing referenced files as not-found errors
- reject schema-invalid documents as data integrity errors

## Manual Content Update Policy (MVP)
- stories/scenes base content is created and modified manually outside app flows
- manual edits must preserve schema and id invariants above
