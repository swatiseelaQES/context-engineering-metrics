import subprocess
import sys
import time
from pathlib import Path


def run_pytest_tests(test_path: str = "generated_tests") -> dict:
    start = time.time()
    Path(test_path).mkdir(parents=True, exist_ok=True)

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q"],
        capture_output=True,
        text=True,
    )

    output = completed.stdout + "\n" + completed.stderr

    return {
        "pytest_exit_code": completed.returncode,
        "pytest_output": output.strip(),
        "execution_duration_ms": int((time.time() - start) * 1000),
        "tests_collected": _extract_collected(output),
        "tests_passed": _extract_passed(output),
        "tests_failed": _extract_failed(output),
    }


def _extract_collected(output: str) -> int:
    passed = _extract_passed(output)
    failed = _extract_failed(output)
    return passed + failed


def _extract_passed(output: str) -> int:
    import re
    match = re.search(r"(\d+)\s+passed", output)
    return int(match.group(1)) if match else 0


def _extract_failed(output: str) -> int:
    import re
    match = re.search(r"(\d+)\s+failed", output)
    return int(match.group(1)) if match else 0