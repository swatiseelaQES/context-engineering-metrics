from pathlib import Path


def write_agent_test_file(agent_name: str, test_code: str) -> str:
    agent_dir = Path("generated_tests") / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    test_file = agent_dir / "test_restful_booker.py"
    test_file.write_text(test_code, encoding="utf-8")

    return str(agent_dir)