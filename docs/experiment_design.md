# Experiment Design

## Experiment: Generate and run Restful Booker API tests

Run:

```bash
python experiments/api_test_generation_workflow.py
```

The experiment evaluates whether contract-grounded generation produces executable API tests.

## Inputs

- `datasets/api_contracts/restful_booker_openapi.yaml`
- `datasets/api_contracts/restful_booker_test_strategy.md`
- OpenAI model configured by `OPENAI_MODEL`

## Outputs

- Generated pytest file
- Raw pytest output
- JSON metrics

## Interpretation

The workflow is considered mature when generated tests are grounded, executable, and measurable without a human copying code between tools.
