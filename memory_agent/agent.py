import time

from shared.config import Settings
from shared.llm.client import OpenAITestGenerationClient
from shared.llm.models import AgentResult
from shared.llm.prompts import triage_prompt
from shared.memory.session_memory import SessionMemory
from shared.retrieval.retriever import KeywordRetriever


class MemoryAgent:
    name = "memory"

    def __init__(self):
        self.retriever = KeywordRetriever([
            "datasets/api_contracts",
            "datasets/release_notes",
            "datasets/knowledge_base",
            "datasets/support_tickets",
        ])
        self.memory = SessionMemory()
        self.memory.add("Prior incident: status enum changes often break downstream automated tests before production symptoms appear.")

    def run(self, task: dict) -> AgentResult:
        start = time.time()
        results = self.retriever.retrieve(task["failure_log"], top_k=3)
        retrieved = "\n\n".join(text for _, text, _ in results)
        memory_context = self.memory.recall(task["failure_log"])
        context = f"Retrieved context:\n{retrieved}\n\nMemory context:\n{memory_context}"
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