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
from metrics.workflow_efficiency.task_completion import task_completion_score
from metrics.workflow_efficiency.tool_invocation_efficiency import tool_invocation_efficiency
from shared.observability.workflow_events import write_trace
from metrics.context_relevance.scoring import context_relevance_score
from metrics.workflow_efficiency.execution_success import execution_success_score


def evaluate_result(result, task):
    output = result.get("output") or result.get("response") or ""
    context = result.get("context", [])
    tool_calls = result.get("tool_calls", [])
    retries = result.get("retries", 0)
    tokens_used = result.get("tokens_used", 0)

    agent_name = result.get("agent") or result.get("agent_name")
    required_context = task.get("required_context", [])
    expected_tools = task.get("expected_tools", [])
    success_criteria = task.get("success_criteria", [])

    completion = task_completion_score(output, success_criteria)

    return {
        "agent": agent_name,
        "context_relevance_score": context_relevance_score(context, required_context),
        "task_completion_score": completion,
        "execution_success_score": execution_success_score(result),
        "needs_human_correction": completion < 0.75,
        "tool_invocation_efficiency": tool_invocation_efficiency(tool_calls, expected_tools),
        "tests_collected": result.get("tests_collected", 0),
        "tests_passed": result.get("tests_passed", 0),
        "tests_failed": result.get("tests_failed", 0),
        "pytest_exit_code": result.get("pytest_exit_code"),
        "retries": retries,
        "tokens_used": tokens_used,
    }


def main():
    task = json.loads(Path("datasets/api_test_generation/restful_booker_create_booking.json").read_text(encoding="utf-8"))
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
    summary_columns = [
        "agent",
        "context_relevance_score",
        "task_completion_score",
        "execution_success_score",
        "tool_invocation_efficiency",
        "tokens_used",
    ]

    print("\n=== AI Workflow Maturity Summary ===\n")
    print(
        df[summary_columns]
        .sort_values(by="execution_success_score", ascending=False)
        .to_string(index=False)
    )

    print("\n=== Execution Details ===\n")

    execution_columns = [
        "agent",
        "tests_collected",
        "tests_passed",
        "tests_failed",
        "pytest_exit_code",
        "retries",
    ]

    print(
        df[execution_columns]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
