from dataclasses import dataclass

@dataclass
class AgentResult:
    agent_name: str
    output: str
    retrieved_context: str
    tools_called: list[str]
    retries: int
    latency_ms: int
    tokens_used: int
