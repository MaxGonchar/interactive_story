# Product Requirements

## Purpose

Interactive Story is a local application for playing and progressing interactive stories. It supports scene-based stories and choice-driven stories, with language models used to generate story content and responses.

The application is for a single user working with story content available on their local machine. Editing the underlying story and character definitions is done outside the application.

## Supported Capabilities

### Stories and scenes

See [`docks/project/scene_driven_story_play.md`](../project/scene_driven_story_play.md) for the full scene-based story play flow, from scene creation through play, correction, and finishing.

### Choice-driven stories

See [`docks/project/choice_driven_story_play.md`](../project/choice_driven_story_play.md) for the full choice-driven story play flow, from choice generation through step selection and branching back.

### Reference data

- The user can view the characters available in a story and choose them when creating a scene.
- The user can view configured language models and use the configured default or select another available model.

## Behavioral Requirements

- A story has one of two progression modes: scene-based or choice-driven. The user experience and progression rules depend on the story's mode.
- A scene is either active or finished. New scene messages, message edits, and message deletions are not accepted for a finished scene.
- Editing a message changes its content without changing its role. Deleting messages does not renumber the remaining message identifiers.
- If a scene-play language-model call fails, the attempted user message and assistant response are not added to scene history.
- Finishing a scene records its summary and prevents further scene play or message changes.
- Returning to an earlier choice-driven step removes steps that follow it.

## Quality Requirements

### Local performance targets

These are target limits for a local environment, excluding frontend rendering and external language-model provider outages where applicable. They are not a claim that performance has been measured or certified.

- Story and scene reads: p95 response time of 500 ms or less.
- Scene play, from user message submission to assistant response: p95 of 20 seconds or less, excluding provider outages.
- Application startup to healthy state: 10 seconds or less.

### Reliability and operations

- Persisted changes must be written atomically so an interrupted write does not leave partial or corrupted story data.
- Invalid requests must receive deterministic client-error responses with useful error details.
- A failed language-model operation must not leave the affected scene or choice progression partially updated.
- Logs must provide structured records for requests, validation failures, persistence failures, and language-model failures.

## Current Limitations

- The application does not create or edit story definitions or character cards; those are prepared outside the application.
- The application is intended for local, single-user use and does not provide multi-user collaboration or account management.

## Domain Terms

- **Story**: a narrative with a title, story type, and progression. Scene-based stories contain ordered scenes; choice-driven stories contain ordered steps.
- **Character**: a story character definition that can be assigned to a scene.
- **Scene**: a playable episode in a scene-based story, with context, writing guidance, participating characters, messages, and an active or finished status.
- **Message**: a user or assistant entry in a scene's ordered conversation.
- **Scene summary**: a summary recorded when a scene is finished and available as context for later scenes.
- **Choice**: an action and its consequence offered as a way to progress a choice-driven story.
- **Step**: a segment of a choice-driven story, containing story text and any choices available to continue.
