import json
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from baseline_agent.agent import BaselineAgent
from rag_agent.agent import RagAgent
from memory_agent.agent import MemoryAgent
from tool_agent.agent import ToolAgent
from orchestration_agent.multi_agent_router import OrchestrationAgent
from metrics.context_relevance.precision import context_precision
from metrics.context_relevance.hallucination_rate import has_unsupported_regression_claim
from metrics.workflow_efficiency.task_completion import task_completion_score
from metrics.workflow_efficiency.tool_invocation_efficiency import tool_invocation_efficiency
from metrics.human_intervention.correction_rate import needs_human_correction
from shared.observability.workflow_events import write_trace
from metrics.context_relevance.scoring import context_relevance_score


def evaluate_result(result, task):
    output = result.get("output") or result.get("response") or ""
    context = result.get("context", [])
    tool_calls = result.get("tool_calls", [])
    retries = result.get("retries", 0)
    tokens_used = result.get("tokens_used", 0)
    agent_name = result.get("agent") or result.get("agent_name")
    required_context = task.get("required_context", [])
    expected_tools = task.get("expected_tools", [])
    expected_root_cause = task.get("expected_root_cause", "")

    return {
        "agent": agent_name,
        "context_relevance_score": context_relevance_score(context, required_context),
        "context_precision": context_precision(context, required_context),
        "has_unsupported_regression_claim": has_unsupported_regression_claim(output, context),
        "task_completion_score": task_completion_score(output, expected_root_cause),
        "needs_human_correction": needs_human_correction(output, expected_root_cause),
        "tool_invocation_efficiency": tool_invocation_efficiency(tool_calls, expected_tools),
        "retries": retries,
        "tokens_used": tokens_used,
    }


def main():
    task = json.loads(Path("datasets/test_failures/failing_api_test.json").read_text(encoding="utf-8"))
    agents = [BaselineAgent(), RagAgent(), MemoryAgent(), ToolAgent(), OrchestrationAgent()]
    rows = []
    for agent in agents:
        result = agent.run(task)

        if not isinstance(result, dict):
            result = result.__dict__

        agent_name = result.get("agent") or result.get("agent_name") or agent.name
        result["agent"] = agent_name

        write_trace(result, f"sample_outputs/traces/{agent_name}.json")
        evaluated = evaluate_result(result, task)
        rows.append(evaluated)

    df = pd.DataFrame(rows)
    output_path = Path("sample_outputs/benchmark_reports/full_system_comparison.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(df[[
        "agent",
        "context_relevance_score",
        "task_completion_score",
        "needs_human_correction",
        "tool_invocation_efficiency",
        "retries",
        "tokens_used",
    ]].to_string(index=False))
    print(f"\nWrote report: {output_path}")


if __name__ == "__main__":
    main()
