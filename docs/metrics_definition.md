# Metrics Definition

## API test generation workflow metrics

| Metric | Definition |
|---|---|
| `context_relevance_score` | Whether the generation workflow used the relevant Restful Booker contract and strategy. |
| `task_completion_score` | `1.0` when pytest exits successfully and discovers tests; otherwise pass ratio when tests are collected. |
| `needs_human_correction` | `true` when generated tests fail or pytest cannot run them. |
| `tool_invocation_efficiency` | `1.0` when orchestration successfully invokes generation and pytest without manual steps. |
| `tokens_used` | Deterministic estimate based on system prompt, user prompt, context, and generated code. |
| `tests_collected` | Number of generated pytest tests discovered. |
| `tests_passed` | Number of generated tests that passed. |
| `tests_failed` | Number of generated tests that failed. |
| `duration_seconds` | End-to-end workflow runtime. |

## Why these metrics matter

A prompt-only workflow may produce plausible test ideas. A context-engineered workflow should produce executable tests, invoke the test runner, and expose objective results.
