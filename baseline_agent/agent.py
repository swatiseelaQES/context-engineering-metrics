from shared.observability.token_usage import workflow_tokens
from shared.tooling.pytest_runner import run_pytest_tests
from shared.tooling.restful_booker_test_templates import baseline_restful_booker_tests
from shared.tooling.test_file_writer import write_agent_test_file


class BaselineAgent:
    name = "baseline"

    def run(self, task):
        context = []
        tool_calls = []

        response = (
            "Generate basic pytest API tests for the requested endpoint. "
            "The tests should send a request and check the response."
        )

        test_code = baseline_restful_booker_tests()
        test_path = write_agent_test_file(self.name, test_code)
        pytest_result = run_pytest_tests(test_path)

        tokens_used = workflow_tokens(
            prompt=task,
            context=context,
            output=response,
            tool_calls=tool_calls,
        )

        return {
            "agent": self.name,
            "output": response,
            "response": response,
            "context": context,
            "tool_calls": tool_calls,
            # TODO: Replace synthetic retry count with actual retry orchestration loop.
            "retries": 1,
            "tokens_used": tokens_used,
            **pytest_result,
        }