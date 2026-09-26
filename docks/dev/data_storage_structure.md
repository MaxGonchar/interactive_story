# Data Storage Structure

## Storage Roots

Story data is stored as YAML under `DATA_ROOT/stories/`. `DATA_ROOT` may be configured in the environment. Relative values are resolved from the `backend/` directory. If unset, the code fallback is the repository's `data-test/` directory; the provided `backend/.env.example` sets `DATA_ROOT=../data`, which resolves to the repository's `data/` directory.

The model registry is stored separately. `MODEL_REGISTRY_PATH` may override its location; relative values are resolved from the repository root. Its default is `data/models.yaml`, regardless of `DATA_ROOT`.

## Layout

```text
<DATA_ROOT>/
  stories/
    <story_id>/
      story.yaml
      characters/
        <character_id>.yaml
      scenes/
        <scene_id>/
          meta.yaml
          messages.yaml
      history.yaml             # choice-driven stories
      llm_usage.yaml           # usage records, when present

<MODEL_REGISTRY_PATH>/         # defaults to repository-root data/models.yaml
```

`<MODEL_REGISTRY_PATH>` above is a file path, not a directory.

The application discovers stories by scanning `stories/` for directories and reading each `story.yaml`; it does not read `stories/index.yaml`. Some checked-in data roots may still contain an older `index.yaml`, but it is not part of the active storage contract. Scene IDs are discovered from numeric directories under `scenes/`; scene status comes from each directory's `meta.yaml`.

## Identifiers and Ordering

- `story_id` is the story directory name and is expected to be a UUID string. It is not repeated in `story.yaml`.
- `scene_id` is the numeric scene directory name and is unique within a story. The next created scene uses one more than the largest existing scene ID, or `1` when none exist.
- `character_id` is the character filename without `.yaml`; it is unique within a story. The storage model does not enforce a particular string format.
- `message_id` is an integer unique within a scene. New messages use one more than the current largest ID; deleting a message does not renumber the others.
- Choice-driven step IDs are stored in `history.yaml`; the next generated step uses one more than the last step ID.
- LLM usage record `id` is a UUID.

Stories are listed by `created_at` descending. Scenes are listed by numeric ID ascending. Messages are returned by message ID ascending. Choice-driven steps retain their order in the `steps` list.

## YAML Documents

### Story metadata

Path: `<DATA_ROOT>/stories/<story_id>/story.yaml`

Every story has the following fields:

```yaml
title: "The Black Harbor"
type: "scene"
created_at: "2024-06-01T12:00:00Z"
```

`type` is `scene` or `choice_driven`. For a choice-driven story, the same file also contains the fields used to generate story steps and choices:

```yaml
title: "The Black Harbor"
type: "choice_driven"
created_at: "2024-06-01T12:00:00Z"
user_character_id: "captain"
character_ids:
  - "navigator"
writing_style: "Cinematic, concise prose."
plot_directions:
  - "Reveal a clue about the harbor."
  - "Introduce a complication for the crew."
```

Story and character content is supplied as YAML. Scene creation and choice-driven play also write application-managed files described below.

### Character card

Path: `<DATA_ROOT>/stories/<story_id>/characters/<character_id>.yaml`

```yaml
name: "Captain Mora"
features:
  appearance: "A sea-worn coat and a scar over the left eyebrow."
  traits:
    - "pragmatic"
    - "suspicious"
memory:
  - "Lost her first crew in a storm."
```

`name` is a string. `features` is a mapping whose values are either strings or lists of strings; it defaults to an empty mapping. `memory` is a list of strings and defaults to an empty list. The character ID comes from the filename, not the document.

### Scene metadata

Path: `<DATA_ROOT>/stories/<story_id>/scenes/<scene_id>/meta.yaml`

```yaml
finished: false
character_ids:
  - "navigator"
user_character_id: "captain"
scene_description:
  general_scene_guide: "Keep tension rising with small discoveries."
  writing_style: "Cinematic, sensory details, concise dialogue."
scene_summary: null
context:
  - "The ship has reached the harbor."
```

- `finished` is a boolean and defaults to `false` when omitted.
- `character_ids` is the list of supporting story character IDs for the scene.
- `user_character_id` is required and may be a character ID or `null`. A null user character is supported only for `scene` stories.
- `scene_description` contains the required `general_scene_guide` and `writing_style` strings.
- `scene_summary` is a list of strings or `null`; it is recorded when the scene is finished.
- `context` is a list of strings or `null`.

The scene ID comes from its directory name, not the YAML document. Scene creation validates that referenced character files exist. The story-level character definitions remain in `characters/`.

### Scene messages

Path: `<DATA_ROOT>/stories/<story_id>/scenes/<scene_id>/messages.yaml`

```yaml
messages:
  - id: 1
    role: "assistant"
    content: "A bell rings through the fog."
    llm_data:
      model_id: "story-model"
  - id: 2
    role: "user"
    content: "I look for the nearest light source."
```

The document contains a `messages` list. Each item has an integer `id`, a `role` of `user` or `assistant`, and string `content`. `llm_data` is optional and, when present, contains the `model_id` used for the assistant response. Missing `messages.yaml` is treated as an empty message list. Play appends the user and assistant messages together; message edit and delete operations rewrite this file while preserving IDs of remaining messages.

### Choice-driven history

Path: `<DATA_ROOT>/stories/<story_id>/history.yaml`

```yaml
steps:
  - id: 1
    incoming_choice: null
    text: "The ship enters the harbor."
    choices:
      - action: "Dock"
        consequence: "The crew is noticed."
  - id: 2
    incoming_choice:
      action: "Dock"
      consequence: "The crew is noticed."
    text: "A harbor guard approaches."
    choices: []
```

Each step has an integer `id`, nullable `incoming_choice`, string `text`, and a `choices` list. A choice contains string `action` and `consequence` fields. Missing `history.yaml` is treated as an empty step list. Editing a step changes its text; returning to a step truncates later steps.

### LLM usage

Path: `<DATA_ROOT>/stories/<story_id>/llm_usage.yaml`

```yaml
calls:
  - id: "44cd72c8-a646-43a0-89d2-0ce256327d2a"
    operation: "scene_reply"
    model_id: "story-model"
    provider_model_id: "provider/model-name"
    provider_created: 1789898289
    duration_ms: 2216
    usage:
      prompt_tokens: 2740
      completion_tokens: 73
      total_tokens: 2813
    cost_usd: 0.001516
    scene_id: 1
    message_id: 19
    step_id: null
```

`calls` is an ordered list. `operation` is one of `scene_reply`, `scene_summary`, `story_generation`, or `choice_generation`. Every record contains a UUID, selected and provider model IDs, provider timestamp, duration, and token usage. `cost_usd` and content references are nullable. Scene operations require `scene_id`; choice generation requires `step_id`; story generation has no scene, message, or step reference. Missing `llm_usage.yaml` is treated as an empty list.

### Model registry

Default path: `<repository-root>/data/models.yaml`.

```yaml
models:
  story-model:
    name: "Story Model"
    providerModelID: "provider/model-name"
    default: true
```

The mapping key is the model ID. `name` and `providerModelID` are required non-empty strings. `default` is a boolean that defaults to `false`; the registry must contain at least one model and exactly one model marked as default.

## Persistence Behavior

- YAML is loaded with `safe_load` and validated against Pydantic storage models.
- Each persisted file write uses a temporary file in the same directory, flushes and `fsync`s it, then replaces the target with `os.replace`.
- Atomic replacement applies to one file at a time. It does not make multi-file operations transactional. Scene creation writes `meta.yaml` and `messages.yaml` separately; interruption between those writes may leave only one of the files updated.
- Scene play persists the user and assistant messages together in one atomic write to `messages.yaml`, after the LLM response succeeds. LLM usage is appended to its own file separately.
- Choice-driven history and LLM usage are each rewritten atomically as individual files. Usage appends are protected by an in-process per-story lock; scene message writes do not use that lock.

## Application-Managed Changes

- Creating a scene creates its scene directory and writes `meta.yaml` and an initial assistant message in `messages.yaml`.
- Playing, editing, regenerating, or deleting messages updates the scene's `messages.yaml`; finishing a scene updates its `meta.yaml` with `finished: true` and the summary.
- Choice-driven generation, editing, and rewind operations update `history.yaml`.
- LLM calls append usage records to `llm_usage.yaml` when usage metadata is available.
- Story definitions and character cards are read from their YAML files; the application does not expose operations to edit those files.
