# UI Response Time Tracking

## Scope
Scene driven story message generating and regenerating functionality, scene summary generating.

## Requirements
- User wants to see how many time response takes from the submit moment or regeneration call
- The implementation should provide a reusable response-time indicator for all in-scope LLM operations.

## Design
- Replace pulsating dots with a dynamic response time indicator.
- Keep the operation verb and display the timer as `Verb MM:SS:MMM`, for example `Sending 00:11:120`.
- Update the displayed time every 10 ms.
- Start timing when the request is initiated by the user and stop timing when it succeeds or fails.
- Apply this to scene message sending, assistant message regeneration, and scene summary generation.
- On failure, hide the timer and keep the existing error message visible.
- Do not persist response times in the backend or YAML storage.
- Keep choice-driven story processing indicators unchanged.
- Do not announce every timer update to assistive technology; provide a throttled completion or failure announcement instead.

## Out of scope:
- storing response times anywhere.
