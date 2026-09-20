# Feature: LLM Usage Statistics

**Status**: Draft  
**Date**: 2026-09-13

## Summary
Record usage data for every successful Venice LLM completion so the application
retains a trustworthy local history of token consumption, provider-reported
cost, and observed request duration. This first iteration collects and stores
the data only; reporting and user-facing statistics are deferred.

## Value
- Makes it possible to understand token use and cost across the LLM models used
  by interactive-story workflows.
- Provides historical data for future comparisons of model cost and performance
  without changing story content or making another provider request.
- Supports the project's local-first, single-user architecture by storing data
  beside the story that caused it.
- Success means every successful LLM completion creates one durable usage record
  containing the selected provider data and application context.

## Scope

In scope for first iteration:
- Collect data for successful (`2xx`) Venice chat-completion requests only.
- Collect every current LLM operation: scene reply, scene summary, story
  generation, and each individual choice-generation call.
- Preserve `prompt_tokens`, `completion_tokens`, `total_tokens`, `cost.usd`,
  and the Venice `created` timestamp.
- Measure and store local end-to-end request duration in milliseconds.
- Append an immutable record to the related story's usage log.
- Preserve usage metadata through the custom LangChain model response.

Out of scope / future:
- Frontend views, dashboards, charts, filters, and exports.
- API endpoints for reading or aggregating usage statistics.
- Recording failed LLM requests, retry attempts, or provider errors.
- Streaming responses and time-to-first-token measurement.
- Cost estimation when Venice omits `cost.usd`.

## User Flow
1. A user triggers an existing story action that requires an LLM completion.
2. The application calls Venice through the existing LangChain integration.
3. When Venice returns a successful response, the application extracts usage,
   cost, model, and provider timestamp metadata.
4. The application measures the complete HTTP request duration locally.
5. The existing story action continues and returns its normal result.
6. The application appends one usage record to the usage log for that story.

There is no user-facing workflow in this iteration. The stored data is intended
for a later statistics feature.

## API Changes
No public REST API endpoints or request/response shapes change in this
iteration.

The internal Venice client response changes from a string to a typed completion
result. `VeniceAIChatModel` then maps that result to LangChain's `AIMessage`:

| Venice response field | LangChain `AIMessage` field |
| --- | --- |
| `usage.prompt_tokens` | `usage_metadata["input_tokens"]` |
| `usage.completion_tokens` | `usage_metadata["output_tokens"]` |
| `usage.total_tokens` | `usage_metadata["total_tokens"]` |
| `cost.usd` | `response_metadata["cost_usd"]` |
| `created` | `response_metadata["provider_created"]` |

Existing callers continue reading `response.content`. LLM clients additionally
read metadata to create the usage record.

## Data Changes

Add one file per story:

```text
data/stories/<story_id>/llm_usage.yaml
```

The file contains an append-only list of successful calls:

```yaml
calls:
  - id: "f58ec747-7004-4d2c-b749-67b8f0c2e845"
    operation: "scene_reply"
    model_id: "default"
    provider_model_id: "zai-org-glm-5-1"
    provider_created: 1739928524
    duration_ms: 1243
    scene_id: 2
    message_id: 17
    usage:
      prompt_tokens: 612
      completion_tokens: 146
      total_tokens: 758
    cost_usd: 0.00042
```

Required fields:
- `id`: application-generated UUID for the stored usage record.
- `operation`: one of `scene_reply`, `scene_summary`, `story_generation`, or
  `choice_generation`.
- `model_id`: the selected application model-registry ID.
- `provider_model_id`: model identifier returned by Venice.
- `provider_created`: Venice Unix timestamp from `created`.
- `duration_ms`: locally measured end-to-end duration, rounded to an integer.
- `usage.prompt_tokens`, `usage.completion_tokens`, and
  `usage.total_tokens`.

Optional fields:
- `cost_usd`: `null` when the successful Venice response does not include
  `cost.usd`.
- Story-content references: `scene_id` and `message_id` for scene operations,
  or `step_id` for choice-driven operations, when applicable.

The log is not changed when story messages are edited, deleted, regenerated, or
when choice-driven history is truncated. It represents completed provider work,
not the current visible story state. Writes use the existing atomic YAML write
strategy.

## Backend Changes
- Add typed internal models for the Venice completion result and usage data.
- Change `VeniceClient` to parse the successful provider response into that
  result instead of returning only content.
- Measure request duration in `VeniceClient` around the non-streaming HTTP
  request.
- Update `VeniceAIChatModel` to construct an `AIMessage` with content,
  normalized `usage_metadata`, and Venice-specific `response_metadata`.
- Add domain and storage models for an LLM usage record and its YAML document.
- Add an `LLMUsageRepository` that appends usage records to a story's
  `llm_usage.yaml` atomically.
- Update scene, summary, story-engine, and choice-engine LLM clients to record
  a successful call with its operation and relevant story-content reference.
- Inject the usage repository through the affected service or LLM-client
  factories, following existing dependency patterns.
- Add focused tests for Venice parsing, LangChain metadata mapping, and
  append-only YAML persistence for each operation type.

## Frontend Changes
None. This iteration has no frontend page, component, API client, or user
interface changes.

## Open Questions
- Determine whether a failure to persist a usage record after a successful LLM
  response should fail the surrounding story operation or be logged while the
  operation succeeds.
- Decide the future read API and presentation once enough usage data exists.
- Decide whether future providers need a provider identifier in addition to the
  model identifiers already stored.

## Risks
- Venice documents `cost` in its response example but does not mark it as
  required; persistence must allow a missing cost.
- Usage metadata must be read immediately from the `AIMessage`; parsers and
  downstream transformations may otherwise discard it.
- Choice generation makes multiple parallel LLM calls, each of which must write
  its own record without overwriting another record.
- The append-only log will grow over time. This is acceptable for local MVP
  usage, but future reporting may need indexing or archived log files.