def triage_prompt(task: dict, context: str = "") -> str:
    return f"""
You are a software quality engineer. Triage the failing test and identify the likely root cause.

Failure log:
{task['failure_log']}

Context:
{context or 'No additional context provided.'}

Return: root cause, supporting evidence, and recommended next action.
""".strip()
