def test_generation_prompt(task: dict) -> str:
    required_context = "\n".join(f"- {item}" for item in task.get("required_context", []))
    success_criteria = "\n".join(f"- {item}" for item in task.get("success_criteria", []))

    return f"""
Generate pytest API tests for the following API workflow.

Goal:
{task.get("goal", "")}

Base URL:
{task.get("base_url", "")}

Endpoint:
{task.get("endpoint", "")}

Required context:
{required_context}

Success criteria:
{success_criteria}
""".strip()