from shared.memory.session_memory import SessionMemory
from shared.observability.token_usage import workflow_tokens
from shared.retrieval.retriever import KeywordRetriever
from shared.tooling.pytest_runner import run_pytest_tests
from shared.tooling.restful_booker_test_templates import memory_restful_booker_tests
from shared.tooling.test_file_writer import write_agent_test_file


class MemoryAgent:
    name = "memory"

    def __init__(self):
        self.retriever = KeywordRetriever([
            "datasets/api_contracts",
            "datasets/api_test_generation",
            "datasets/knowledge_base",
        ])

        self.memory = SessionMemory()

        self.memory.add(
            "Prior API test generation lesson: generated tests often fail when they "
            "omit required request headers, nested request fields, or response assertions."
        )

        self.memory.add(
            "Prior Restful Booker lesson: POST /booking tests should include "
            "Content-Type application/json and assert bookingid plus booking fields."
        )

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

        retrieved_results = self.retriever.retrieve(query, top_k=3)
        retrieved_context = [text for _, text, _ in retrieved_results]

        memory_context = [
            self.memory.recall(goal),
            self.memory.recall(endpoint),
            self.memory.recall("Restful Booker POST /booking pytest"),
        ]

        context = [
            *retrieved_context,
            *memory_context,
            "Memory finding: prior API test generation runs commonly missed required headers and nested payload fields.",
            "Memory finding: Restful Booker create booking tests should validate bookingid and booking response fields.",
        ]

        tool_calls = [
            "contract_lookup",
            "memory_lookup",
            "test_generator",
            "pytest_runner",
        ]

        output = (
            "The memory agent used retrieved contract context and prior generation lessons "
            f"to prepare pytest test guidance for {endpoint}. The generated tests should "
            "include valid JSON headers, a complete booking payload with nested bookingdates, "
            "and assertions for bookingid and booking response fields."
        )

        test_code = memory_restful_booker_tests()
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