## General story storage structure

Character-driven stories follow the existing scene-driven story layout. There is no separate top-level storage root or parallel story directory structure.

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
			llm_usage.yaml
```

### Shared story files

- `story.yaml` stores story-level metadata and identifies the story type.
- `characters/` stores the character definitions and memories shared by the story's scenes.
- `llm_usage.yaml` stores usage records for LLM calls made during the story.

#### `story.yaml`

For a character-driven story, `story.yaml` contains the story title, type, and creation time:

```yaml
title: "The Black Harbor"
type: "character_driven"
created_at: "2026-10-05T12:00:00Z"
```

Existing `scene` and `choice_driven` stories retain their current `story.yaml` fields. The `character_driven` story type adds no story-level fields beyond its type identifier.

#### Character file

Each character has a separate file under `characters/`. The character ID is the filename without `.yaml`. Character-driven stories can keep the existing `name`, `features`, and `memory` shape while using consistent feature keys for the character agent's profile:

```yaml
name: "Captain Mora"
features:
	appearance: "A sea-worn coat and a scar over the left eyebrow."
	personality_traits:
		- "pragmatic"
		- "suspicious"
	background:
		- "Lost her first crew in a storm."
	goals:
		- "Keep the current crew alive."
	voice: "Direct, guarded, and economical with words."
memory:
	- "Distrusts the harbor master after being betrayed by a port official."
```

`features` describes the character profile used to ground their agent. `memory` holds the character's current accumulated memories across scenes; it is separate from the stable profile so scene outcomes can update memory without rewriting character identity.

### Scene files

#### `scenes/<scene_id>/meta.yaml`

For a character-driven scene, `meta.yaml` stores its setup and lifecycle data, including the scene summary:

```yaml
finished: false
character_ids:
	- "navigator"
user_character_id: null
scene_description:
	general_scene_guide: "Keep tension rising with small discoveries."
	writing_style: "Cinematic, sensory details, concise dialogue."
context:
	- "The ship has reached the harbor."
scene_summary: null
```

`character_ids` lists the NPCs participating in the scene and available for the player to trigger. `user_character_id` optionally identifies a character controlled directly by the player; when it is `null`, no player character is assigned and the scene can be played using NPCs only. `scene_summary` is populated when the scene is finished. Agent model IDs are recorded on the corresponding messages, not in scene metadata. Character memory updates are written to each character's `memory` field and are not duplicated in `meta.yaml`.

#### `scenes/<scene_id>/messages.yaml`

For a character-driven scene, each entry represents one scene turn. It groups the player's input or character trigger, any generated character action, and the narrator's resulting paragraph:

```yaml
messages:
  - id: 1
    narration: "A bell rings through the fog."
    llm_data:
      character_model_id: "character-model"
      narrator_model_id: "narrator-model"
  - id: 2
    input:
      action: "I look for the nearest light source."
      author: "captain"
    narration: "You turn toward a wavering glow at the end of the pier."
    llm_data:
      character_model_id: null
      narrator_model_id: "narrator-model"
  - id: 3
    input:
      author: "navigator"
      guidance: "Warn the captain about the harbor master."
      action: "The navigator leans close and warns the captain."
    narration: "The navigator catches your sleeve. 'The harbor master knows we are here,' she whispers."
    llm_data:
      character_model_id: "character-model"
      narrator_model_id: "narrator-model"
```

An opening narration has no `input`. For later turns, `input.action` stores text supplied by the player, `input.author` identifies the acting character, and `input.guidance` optionally steers a triggered NPC. The author is the player-controlled character ID for a player action or an NPC ID for a character trigger; it is null for a player action when the scene has no player character. `action` stores the character agent's generated contribution separately from `narration`, the narrator's final paragraph for the scene. The agent's raw response (including any `INTERNAL` field) is stored as returned, without parsing. Keeping them separate preserves the generated action for correction and regeneration without requiring a decision here about how each is presented in the UI. `llm_data` is present on every entry. For turns it records the models used: `character_model_id` is null when no character agent generated an action, while `narrator_model_id` records the model that generated the narration. For the opening entry it records the two models selected at scene creation, which become the scene's initial model defaults.

Each stored entry represents a completed turn with all of its LLM work finished; in-progress turns are not written to `messages.yaml`. Correcting or regenerating a turn updates its entry; deleting the last turn removes that entry. IDs remain ordered and are not renumbered when the last turn is deleted; the next created entry uses the maximum remaining ID plus one, so a deleted ID can be reused. The opening entry cannot be deleted.

### `llm_usage.yaml`

`llm_usage.yaml` remains at the story root and stores one record per actual LLM call. Calls that contribute to the same message have the same `scene_id` and `message_id`, with `operation` distinguishing the character-agent call from the narrator call:

```yaml
calls:
	- id: "44cd72c8-a646-43a0-89d2-0ce256327d2a"
		operation: "character_action"
		model_id: "character-model"
		provider_model_id: "provider/character-model"
		provider_created: 1789898289
		duration_ms: 1600
		usage:
			prompt_tokens: 1800
			completion_tokens: 120
			total_tokens: 1920
		cost_usd: null
		scene_id: 1
		message_id: 3
		character_id: "navigator"
		step_id: null
	- id: "f1377f60-fbe2-43ce-aed9-ad799705eeba"
		operation: "narration"
		model_id: "narrator-model"
		provider_model_id: "provider/narrator-model"
		provider_created: 1789898291
		duration_ms: 2100
		usage:
			prompt_tokens: 2400
			completion_tokens: 95
			total_tokens: 2495
		cost_usd: null
		scene_id: 1
		message_id: 3
		character_id: null
		step_id: null
```

Player-authored input has no character-agent usage record; its narrator call still gets a usage record linked to the message. Usage records for a turn are written only after the turn is persisted, so a failed turn leaves none. Summary and memory-update calls use the configured `SUMMARY_MODEL`. Scene-finish calls such as summary generation and character memory updates use `scene_id` with `message_id: null`; memory-update records also identify the affected `character_id`. This adds character-driven operations (for example, `character_action`, `narration`, `scene_summary`, and `character_memory_update`) and an optional `character_id` reference to the existing usage record format. The model and token details remain in `llm_usage.yaml`; each message's `llm_data` keeps the concise model IDs used for that turn.

## Storage model design

Storage models validate the persisted format selected by the parent story type. Existing `scene` and `choice_driven` data remains valid; character-driven data adds its own scene and message shapes without a per-message discriminator.

### Type aliases

Extend the existing domain aliases to include the new story type and call operations:

```python
StoryType = Literal["scene", "choice_driven", "character_driven"]
LLMUsageOperation = Literal[
	"scene_reply",
	"scene_summary",
	"story_generation",
	"choice_generation",
	"character_action",
	"narration",
	"character_memory_update",
]
```

`StoryYaml` remains the story metadata model; no character-driven-only story fields are needed. `CharacterYaml` is also reused unchanged: profile conventions such as `appearance`, `personality_traits`, `background`, `goals`, and `voice` remain keys inside `features`.

### Scene metadata models

Character-driven scenes use the existing `SceneMetadataYaml` directly. Its fields already cover the scene participants, optional player character, scene description, context, finished state, and summary. There is no `CharacterDrivenSceneMetadataYaml` subclass: model IDs belong to message records, and character memory is persisted only in character files. Character IDs still require repository-level checks against the story's character files.

### Character-driven messages

Keep the current `MessageYaml` and `MessagesYaml` for scene-driven conversation data. The character-driven shape is independent because it represents an entire turn rather than a role/content chat message:

```python
class CharacterDrivenInputYaml(BaseModel):
	action: str
	author: str | None
	guidance: str | None = None


class CharacterDrivenLLMDataYaml(BaseModel):
	character_model_id: str | None
	narrator_model_id: str


class CharacterDrivenMessageYaml(BaseModel):
	id: int
	input: CharacterDrivenInputYaml | None = None
	narration: str
	llm_data: CharacterDrivenLLMDataYaml


class CharacterDrivenMessagesYaml(BaseModel):
	messages: list[CharacterDrivenMessageYaml]
```

An absent `input` identifies the opening narration. For other entries, `input.action` is required: it is the player's action for a user-controlled character or the generated action for an NPC. `input.author` identifies that character; it is null for a player action when the scene has no player character (`user_character_id` is null). `guidance` is optional. `llm_data.character_model_id` is required but nullable; for turns the repository validates it is null for a player action and populated for an NPC author, and the opening entry stores the model IDs selected at scene creation. `llm_data.narrator_model_id` is always required. Cross-file author validation uses the scene's `user_character_id` and `character_ids`: a null author is valid only when `user_character_id` is null, and an NPC author must be in `character_ids`. A turn is a player turn if `author` is null or equals `user_character_id`, and a character turn otherwise.

The repository selects `CharacterDrivenMessagesYaml` from the story type. Do not combine the legacy and character-driven message shapes into one model with numerous optional fields.

### LLM usage models

Retain one `LLMUsageYaml` / `LLMUsageDocumentYaml` format and add nullable character attribution:

```python
class LLMUsageYaml(BaseModel):
	id: UUID
	operation: LLMUsageOperation
	model_id: str
	provider_model_id: str
	provider_created: int = Field(ge=0)
	duration_ms: int = Field(ge=0)
	usage: TokenUsageYaml
	cost_usd: float | None = Field(default=None, ge=0)
	scene_id: int | None = Field(default=None, ge=1)
	message_id: int | None = Field(default=None, ge=1)
	step_id: int | None = Field(default=None, ge=1)
	character_id: str | None = None
```

Operation-specific validation keeps the current rules and adds these character-driven cases:

- `character_action` and `narration` require `scene_id` and `message_id`, and forbid `step_id`.
- `character_action` requires `character_id`; `narration` has no character attribution.
- `character_memory_update` requires `scene_id` and `character_id`, and forbids `message_id` and `step_id`.
- `scene_summary` continues to require `scene_id` and forbid `message_id` and `step_id`.

The repository selects schemas by story type; inheritance is used only where persisted fields share their meaning, while different message formats remain explicit and independently validated.
