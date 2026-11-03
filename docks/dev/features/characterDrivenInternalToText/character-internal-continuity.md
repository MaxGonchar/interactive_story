# Feature: Character Internal Continuity

**Status**: Draft  
**Date**: 2026-11-03

## Summary
LLM characters currently lose their emotional trajectory between turns, because the next-turn context contains only narrator paragraphs and the character's private `INTERNAL` thoughts are never fed back. This feature makes the character agent return structured JSON, stores its fields separately, and adds a character's own `INTERNAL` text to the context used for that character's next turn and for its end-of-scene memory generation. It also fixes a context leak where the memory agent currently receives every actor's raw output, including other characters' `INTERNAL` text.

## Value
- Problem: the NPC's emotional curve resets each turn; memories are produced without the character's inner state.
- Fits the core purpose: more coherent, believable character-driven scenes.
- Success criteria:
  - A character's next action reflects its previous internal thoughts (see `characterDrivenInternalToText/feature.md`, Ember example).
  - A character's context never contains another character's `INTERNAL`.
  - `INTERNAL` never appears in any API response or the UI.

## Scope
In scope, delivered in two phases:

1. **Phase 1 - structured output.** The character agent returns JSON; fields are stored separately; rendered text for the narrator and API is unchanged.
2. **Phase 2 - context injection.** Own `INTERNAL` is added to the character agent context and memory agent context.

Out of scope:
- Showing internals in the UI.
- `INTERNAL` for the player's character (player turns remain free text with `action` only).
- Retry or fallback on JSON parse failure.
- Migration of existing data (feature is in testing).
- Changes to the narrator's context: it still receives narration only, plus the current turn.

## User Flow
No user-visible change. The player triggers a character turn as today; the generated narration is shown as today. Quality improves because the character agent now sees its own earlier internal thoughts.

## API Changes
None. `character_action` in `docks/dev/endpoints.md` remains a plain string with the same `INTERNAL: ... ACTION: ... SPEECH: ... TONE: ...` rendering, produced from the stored fields. It is not displayed by the frontend. `internal` is not added to any response schema.

## Data Changes
The stored input for a character turn (`messages.yaml`) gains optional fields:

```yaml
input:
  author: ember
  guidance: null
  internal: "He's just a dog..."
  action: "Ember exhales slowly..."
  speech: "\"Hey, Max.\""
  tone: "Outwardly calm, internally tense"
```

- Character turns store `internal`, `action`, `speech`, `tone` as separate strings.
- Player turns store only `action`.
- Old turns (action as a raw blob, no `internal`) stay valid; the absence of `internal` means nothing is injected.

## Backend Changes
- `models/domain.py`, `models/storage.py`: `CharacterDrivenInput` / `CharacterDrivenInputYaml` gain optional `internal`, `speech`, `tone`.
- `llm/character_agent_client.py`: parse the response with `PydanticOutputParser` into a `CharacterTurnOutput` model (`internal`, `action`, `speech`, `tone`). A parse failure or empty response raises `LLMError`; the turn fails and the user retries.
- `llm/templates/character_driven/character_agent_system.j2`: replace the labeled text format and example with `{{ format_instructions }}` and a JSON example; explain that `**INTERNAL:**` blocks in the scene context are the character's own earlier private thoughts (phase 2).
- `llm/prompt_builder.py`:
  - add a renderer that builds the four-field text (`**INTERNAL:** / **ACTION:** / **SPEECH:** / **TONE:**`) from stored fields, used for `current_turn` and `character_action`;
  - phase 2: build the character agent's scene context per character, emitting `**INTERNAL:** ...` before the narration of each message authored by that character when `internal` is present;
  - phase 2: `build_scene_transcript` / `build_memory_agent_context` become per-character, so only the memory owner's `INTERNAL` is included and other actors' internals are stripped.
- `services/character_driven_scene_turn_service.py`: build `GeneratedItem`/`CharacterDrivenInput` from the parsed fields; pass the rendered text to the narrator as `current_turn` (unchanged content); pass the acting character to the context builder in phase 2.
- `api/routers/character_play.py`: `character_action` is rendered from stored fields (with fallback to `action` for old blobs).
- Memory generation (`character_driven_scene_memory_service.py`, `memory_agent_client.py`): use the per-character transcript.
- `llm/templates/character_driven/memory_agent_system.j2`: mention that `**INTERNAL:**` blocks are the character's own private thoughts.

## Frontend Changes
None.

## Documentation Updates
- `docks/dev/data_storage_structure.md`: update the character-driven message example (around line 160) and the paragraph at line 169 to describe the separate `internal`, `action`, `speech`, `tone` fields on character inputs, and that old turns may hold a raw `action` blob.
- `docks/dev/endpoints.md`: line 440 says the character action is "retained unparsed"; change it to say it is produced by the character agent as structured fields and returned rendered as text in `character_action`, with `internal` never exposed separately. The example at line 430 stays valid.
- `docks/dev/requirements.md`: around line 23, add that a character's own internal thoughts from earlier turns are used as context for its next turns and its memory generation, and are never shown to other characters or the player.
- `docks/project/`: review for character-driven behavior descriptions (only `scene_driven_story_play.md` and `choice_driven_story_play.md` exist; neither describes character-driven turns, so no change is expected).
- `docks/dev/progect_structure.md`: no change expected, since no modules are added.

## Open Questions
- Exact name of the parsed output model and whether `speech`/`tone` are required or optional in the LLM schema.
- Whether the rendered `character_action` for old blob-style turns should simply return the stored `action` unchanged.

## Risks
- The model may return invalid JSON or wrap it in fences; with no retry, such turns fail with `llm_error` and the user must retry. Monitor frequency.
- Longer context from injected internals increases token usage and cost.
- The character may leak or repeat its own internals in speech or action; the system prompt must say they are private.
- Narrator may still reveal `INTERNAL` from `current_turn`; this relies on the existing prompt rule 7.
- Mixed data: old turns have no structured fields, so continuity applies only to new turns.
