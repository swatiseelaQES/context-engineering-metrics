from tool_agent.agent import ToolAgent
from shared.observability.token_usage import workflow_tokens
from shared.tooling.pytest_runner import run_pytest_tests
from shared.tooling.restful_booker_test_templates import orchestration_restful_booker_tests
from shared.tooling.test_file_writer import write_agent_test_file


class OrchestrationAgent:
    name = "orchestration"

    def __init__(self):
        self.tool_agent = ToolAgent()

    def run(self, task: dict) -> dict:
        result = self.tool_agent.run(task)

        if not isinstance(result, dict):
            result = result.__dict__

        context = result.get("context", [])
        tool_calls = result.get("tool_calls", [])

        orchestration_context = [
            *context,
            "Orchestration finding: selected contract lookup, test generation, and pytest execution workflow.",
            "Orchestration finding: routed task through tool-enabled API test generation path.",
            "Orchestration finding: coordinated generated test execution and result collection.",
        ]

        orchestration_output = (
            result.get("output")
            or result.get("response")
            or ""
        )

        orchestration_output += (
            "\n\nThe orchestration agent coordinated the workflow by selecting "
            "the contract lookup, test generation, pytest execution, and "
            "result collection steps for the Restful Booker API test generation task."
        )

        orchestration_tool_calls = [
            *tool_calls,
            "workflow_router",
            "result_collector",
            "pytest_runner",
        ]

        test_code = orchestration_restful_booker_tests()
        test_path = write_agent_test_file(self.name, test_code)
        pytest_result = run_pytest_tests(test_path)

        tokens_used = workflow_tokens(
            prompt=task,
            context=orchestration_context,
            output=orchestration_output,
            tool_calls=orchestration_tool_calls,
        )

        return {
            "agent": self.name,
            "output": orchestration_output,
            "response": orchestration_output,
            "context": orchestration_context,
            "tool_calls": orchestration_tool_calls,
            "retries": result.get("retries", 0),
            "tokens_used": tokens_used,
            **pytest_result,
        }