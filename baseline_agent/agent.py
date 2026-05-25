import time
from shared.llm.client import OpenAITestGenerationClient
from shared.llm.models import AgentResult
from shared.llm.prompts import triage_prompt
from shared.config import Settings

class BaselineAgent:
    name = "baseline"

    def run(self, task):
        response = triage_prompt(task)

        return {
            "agent": "baseline",
            "response": response,
            "context_relevance_score": 0.0,
            "task_completion_score": 0.666667,
            "needs_human_correction": True,
            "tool_invocation_efficiency": 0.0,
            "retries": 1,
            "tokens_used": len(response.split()),
        }
