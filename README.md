# Context Engineering Metrics

**GitHub description:** Measure AI workflow maturity by generating, running, and evaluating API tests with prompt-only, RAG, memory, tool, and orchestration patterns.

This repository demonstrates how teams can move from prompt engineering to measurable context engineering. The main demo uses OpenAI to generate pytest API tests from a Restful Booker contract, runs those tests against `https://restful-booker.herokuapp.com`, and collects metrics from the workflow.

## Why this repo exists

Most AI workflow demos stop at “the model answered.” Mature engineering teams need better signals:

- Was the answer grounded in the right context?
- Did the workflow retrieve the relevant contract and test strategy?
- Did the generated tests actually run?
- How many tests passed or failed?
- Did a human need to correct the generated code?
- Did orchestration reduce manual glue work?

This repo treats AI workflows as observable software systems.

## Primary demo: OpenAI-generated API tests for Restful Booker

The orchestration flow is:

```text
Restful Booker contract + test strategy
        ↓
OpenAI test generation agent
        ↓
generated pytest module
        ↓
pytest execution against Restful Booker
        ↓
metrics collection and run artifacts
```

The generated tests cover:

- `GET /ping` health check
- `GET /booking` booking IDs list
- `POST /booking` create booking
- `GET /booking/{id}` read booking
- `POST /auth` create token
- `PATCH /booking/{id}` partial update
- `DELETE /booking/{id}` cleanup

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your OpenAI API key to `.env`, or export it in your shell:

```bash
export OPENAI_API_KEY=your_key_here
```

If no `OPENAI_API_KEY` is available, the repo uses a deterministic fallback test template. This keeps the orchestration and metrics demo runnable in CI.

## SSL verification

This repo defaults SSL verification to `false` for both OpenAI and Restful Booker calls because the demo is designed to run in environments where corporate SSL inspection may break local experimentation.

```text
OPENAI_VERIFY_SSL=false
RESTFUL_BOOKER_VERIFY_SSL=false
```

For production systems, prefer SSL verification enabled.

## Original maturity comparison demo

You can still run the original comparison across agent maturity levels:

```bash
python experiments/full_system_comparison.py
```

That writes:

```text
sample_outputs/benchmark_reports/full_system_comparison.csv
```

## Repo progression

```text
baseline_agent          static prompt only
rag_agent               prompt + retrieved context
memory_agent            RAG + reusable session memory
tool_agent              memory + tool calls
orchestration_agent     planner + context builder + routing + pytest execution
test_generation         OpenAI prompt templates and generated pytest module creation
metrics                 reusable quality and workflow metrics
experiments             comparison and API workflow scripts
```

## Example metrics

| Metric | What it measures |
|---|---|
| Context relevance score | Whether the workflow used the right contract and strategy context |
| Task completion score | Whether generated tests ran successfully |
| Tool invocation efficiency | Whether orchestration invoked generation and pytest correctly |
| Tests collected | Number of pytest tests discovered |
| Tests passed / failed | Execution result quality |
| Tokens used | Estimated prompt + context + generated-code size |
| Duration | End-to-end workflow runtime |


Core argument:

> Prompt engineering optimizes individual interactions. Context engineering operationalizes the system around the model. Mature AI workflows need metrics, observability, and repeatable evaluation.

## License

MIT
