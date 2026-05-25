import time
from pathlib import Path

from shared.config import Settings
from shared.llm.client import OpenAITestGenerationClient
from shared.llm.models import AgentResult
from shared.llm.prompts import triage_prompt
from shared.retrieval.retriever import KeywordRetriever
from shared.tooling.log_parser_tool import extract_unexpected_status
from shared.tooling.api_tool import is_valid_status


class ToolAgent:
    name = "tool"

    def __init__(self):
        self.retriever = KeywordRetriever([
            "datasets/api_contracts",
            "datasets/release_notes",
            "datasets/knowledge_base",
            "datasets/support_tickets",
        ])

    def run(self, task: dict) -> AgentResult:
        start = time.time()
        tools_called = []
        unexpected_status = extract_unexpected_status(task["failure_log"])
        tools_called.append("log_parser_tool")

        contract_text = Path("datasets/api_contracts/orders_api.md").read_text(encoding="utf-8")
        valid = is_valid_status(unexpected_status or "", contract_text)
        tools_called.append("api_tool")

        results = self.retriever.retrieve(task["failure_log"] + " " + (unexpected_status or ""), top_k=4)
        retrieved = "\n\n".join(text for _, text, _ in results)
        tool_context = f"Tool findings: unexpected_status={unexpected_status}; status_valid_in_contract={valid}"
        context = f"{retrieved}\n\n{tool_context}"
        OpenAITestGenerationClient(Settings())
        response = triage_prompt(task)
        response_text = response.text if hasattr(response, "text") else str(response)
        tokens_used = response.tokens_used if hasattr(response, "tokens_used") else len(response_text.split())

        return AgentResult(
            self.name,
            response_text,
            context,
            [],
            0,
            int((time.time() - start) * 1000),
            tokens_used
        )