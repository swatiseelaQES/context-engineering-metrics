from shared.llm.prompts import test_generation_prompt
from shared.observability.token_usage import workflow_tokens
from shared.retrieval.retriever import KeywordRetriever
from shared.tooling.pytest_runner import run_pytest_tests
from shared.tooling.restful_booker_test_templates import rag_restful_booker_tests
from shared.tooling.test_file_writer import write_agent_test_file


class RagAgent:
    name = "rag"

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

        query = " ".join([
            goal,
            endpoint,
            base_url,
            " ".join(required_context),
        ])

        results = self.retriever.retrieve(query, top_k=3)
        retrieved_context = [text for _, text, _ in results]

        context = [
            *retrieved_context,
            "RAG finding: retrieved Restful Booker contract and API test generation guidance.",
        ]

        tool_calls = [
            "contract_lookup",
            "test_generator",
            "pytest_runner",
        ]

        response = (
            test_generation_prompt(task)
            + "\n\nRAG test generation guidance: Generate pytest API tests for "
              f"{endpoint}. Use retrieved contract context to include valid JSON headers, "
              "a complete booking payload, and assertions for bookingid and booking fields."
        )

        test_code = rag_restful_booker_tests()
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
            "retries": 0,
            "tokens_used": tokens_used,
            **pytest_result,
        }