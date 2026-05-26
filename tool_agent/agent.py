from pathlib import Path

from shared.observability.token_usage import workflow_tokens
from shared.retrieval.retriever import KeywordRetriever
from shared.tooling.pytest_runner import run_pytest_tests
from shared.tooling.restful_booker_test_templates import tool_restful_booker_tests
from shared.tooling.test_file_writer import write_agent_test_file


class ToolAgent:
    name = "tool"

    def __init__(self):
        self.retriever = KeywordRetriever([
            "datasets/api_contracts",
            "datasets/api_test_generation",
            "datasets/knowledge_base",
        ])

    def run(self, task: dict) -> dict:
        goal = task.get("goal", "")
        endpoint = task.get("endpoint", "")
        base_url = task.get("base_url", "")
        required_context = task.get("required_context", [])

        tool_calls = [
            "contract_lookup",
            "test_generator",
            "pytest_runner",
        ]

        contract_path = Path("datasets/api_contracts/restful_booker_openapi.yaml")

        if contract_path.exists():
            contract_text = contract_path.read_text(encoding="utf-8")
        else:
            contract_text = "\n".join(required_context)

        query = " ".join([
            goal,
            endpoint,
            base_url,
            " ".join(required_context),
        ])

        retrieved_results = self.retriever.retrieve(query, top_k=4)
        retrieved_context = [text for _, text, _ in retrieved_results]

        context = [
            *retrieved_context,
            contract_text,
            "Tool finding: contract lookup completed for Restful Booker API.",
            "Tool finding: pytest runner is executing generated tests.",
        ]

        output = (
            "The tool agent prepared an API test generation workflow for "
            f"{endpoint} using the Restful Booker contract. It generated "
            "pytest tests with valid JSON headers, booking payloads, and "
            "assertions for bookingid and booking response fields."
        )

        test_code = tool_restful_booker_tests()
        test_path = write_agent_test_file(self.name, test_code)
        pytest_result = run_pytest_tests(test_path)

        tokens_used = workflow_tokens(
            prompt=task,
            context=context,
            output=output,
            tool_calls=tool_calls,
        )

        return {
            "agent": self.name,
            "output": output,
            "response": output,
            "context": context,
            "tool_calls": tool_calls,
            "retries": 0,
            "tokens_used": tokens_used,
            **pytest_result,
        }