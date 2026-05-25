# Architecture

The repo now centers on an API-test-generation workflow. The workflow demonstrates context engineering because the model does not generate tests from a vague instruction alone. It receives a concrete API contract and test strategy, produces pytest code, invokes a real test runner, and records the result as operational metrics.

```text
datasets/api_contracts/restful_booker_openapi.yaml
datasets/api_contracts/restful_booker_test_strategy.md
        ↓
test_generation/generate_tests.py
        ↓
generated_tests/test_restful_booker_generated.py
        ↓
orchestration_agent/api_test_orchestrator.py
        ↓
pytest + RestfulBookerClient
        ↓
sample_outputs/api_test_runs/latest_metrics.json
```

## Key design choices

- Contract context is explicit and versionable.
- Generated code is saved, not hidden inside a chat transcript.
- Tests are executed by pytest, not manually inspected.
- Results are converted into metrics.
- SSL verification is controlled through environment variables.
