from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from shared.config import Settings, get_settings
from test_generation.generate_tests import generate_restful_booker_tests


@dataclass
class ApiTestRunMetrics:
    agent: str
    generated_test_file: str
    used_openai: bool
    context_relevance_score: float
    task_completion_score: float
    needs_human_correction: bool
    tool_invocation_efficiency: float
    retries: int
    tokens_used: int
    tests_collected: int
    tests_passed: int
    tests_failed: int
    duration_seconds: float
    pytest_exit_code: int


def _parse_pytest_output(output: str) -> tuple[int, int, int]:
    collected = passed = failed = 0
    for line in output.splitlines():
        line = line.strip()
        if " collected" in line and line.startswith("collected "):
            try:
                collected = int(line.split()[1])
            except Exception:
                pass
        if " passed" in line or " failed" in line:
            parts = line.replace(",", "").split()
            for index, part in enumerate(parts[:-1]):
                if part.isdigit() and parts[index + 1].startswith("passed"):
                    passed = int(part)
                if part.isdigit() and parts[index + 1].startswith("failed"):
                    failed = int(part)
    if collected == 0:
        collected = passed + failed
    return collected, passed, failed


def run_generated_api_tests(settings: Settings | None = None, root: Path | None = None) -> ApiTestRunMetrics:
    settings = settings or get_settings()
    root = root or Path.cwd()

    start = time.perf_counter()
    generation = generate_restful_booker_tests(settings=settings, root=root)

    command = [sys.executable, "-m", "pytest", str(generation.path), "-q"]
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    duration = time.perf_counter() - start
    collected, passed, failed = _parse_pytest_output(completed.stdout)

    task_completion = 1.0 if completed.returncode == 0 and collected > 0 else (passed / collected if collected else 0.0)
    metrics = ApiTestRunMetrics(
        agent="api-test-orchestration",
        generated_test_file=str(generation.path),
        used_openai=generation.used_openai,
        context_relevance_score=1.0,
        task_completion_score=task_completion,
        needs_human_correction=completed.returncode != 0,
        tool_invocation_efficiency=1.0,
        retries=0,
        tokens_used=generation.tokens_estimated,
        tests_collected=collected,
        tests_passed=passed,
        tests_failed=failed,
        duration_seconds=round(duration, 3),
        pytest_exit_code=completed.returncode,
    )

    output_dir = root / "sample_outputs" / "api_test_runs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "latest_pytest_output.txt").write_text(completed.stdout)
    (output_dir / "latest_metrics.json").write_text(json.dumps(asdict(metrics), indent=2))
    return metrics


def main() -> None:
    metrics = run_generated_api_tests()
    print(json.dumps(asdict(metrics), indent=2))


if __name__ == "__main__":
    main()
