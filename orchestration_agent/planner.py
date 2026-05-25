def choose_workflow(task: dict) -> str:
    if "endpoint=" in task.get("failure_log", ""):
        return "api_test_triage"
    return "general_triage"
