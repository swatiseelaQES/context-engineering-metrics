from shared.llm.prompts import triage_prompt
from shared.observability.token_usage import workflow_tokens


class BaselineAgent:
    name = "baseline"

    def run(self, task):
        context = []
        tool_calls = []

        response = triage_prompt(task)

        tokens_used = workflow_tokens(
            prompt=task,
            context=context,
            output=response,
            tool_calls=tool_calls,
        )

        return {
            "agent": self.name,
            "response": response,
            "context": context,
            "tool_calls": tool_calls,
            "retries": 1,
            "tokens_used": tokens_used,
        }