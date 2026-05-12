# Task 038: Prompt Builder

**Feature:** M5 — LLM Adapter
**Status:** TODO

## Description

Implement `PromptBuilder`, a pure function class that assembles the system prompt string from a `SceneContext`. No I/O, no LLM calls — takes structured domain data, returns a formatted string.

## Scope

What IS included:
- `PromptBuilder` class with:
  - `build_system_prompt(self, context: SceneContext) -> str` — assembles a multi-section system prompt including:
    - Scene description (`entry_point`, `general_scene_guide`, `writing_style`)
    - Character cards (name, appearance, traits, speech patterns, body language, likes, fears, memory entries if present)
    - Message history formatted as a readable transcript
- Prompt is plain text (no XML, no JSON); sections delimited by headers

What is NOT included (deferred):
- Token counting or truncation
- Prompt versioning
- Few-shot examples
- Prompt templating via LangChain `PromptTemplate`

## Deliverable

`backend/app/llm/prompt_builder.py` — a finished `PromptBuilder` class.

```
backend/app/llm/prompt_builder.py
```

## Acceptance Criteria

- [ ] `PromptBuilder().build_system_prompt(context)` returns a non-empty string
- [ ] The returned string contains the scene `entry_point` text
- [ ] The returned string contains each character's `name`
- [ ] The returned string contains each message's `content` from `context.messages`
- [ ] Calling with an empty `characters` list and empty `messages` list does not raise

## Test Notes

Unit tests with hardcoded `SceneContext` fixtures (no file I/O). Assert substrings appear in the output. Test edge cases: no characters, no messages, character with all optional fields `None`.

## Dependencies

035
