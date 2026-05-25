from tool_agent.agent import ToolAgent


class OrchestrationAgent:
    name = "orchestration"

    def run(self, task: dict):
        result = ToolAgent().run(task)
        result.agent_name = self.name
        return result
