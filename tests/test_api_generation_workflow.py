from __future__ import annotations

from metrics.workflow_efficiency.api_test_metrics import pass_rate
from orchestration_agent.api_test_orchestrator import _parse_pytest_output
from test_generation.generate_tests import strip_markdown_fences


def test_strip_markdown_fences():
    assert strip_markdown_fences("```python\nprint('x')\n```") == "print('x')\n"


def test_parse_pytest_output_passed():
    output = "collected 3 items\n\n...\n3 passed in 1.23s"
    assert _parse_pytest_output(output) == (3, 3, 0)


def test_parse_pytest_output_failed():
    output = "collected 3 items\n\nF..\n1 failed, 2 passed in 1.23s"
    assert _parse_pytest_output(output) == (3, 2, 1)


def test_pass_rate():
    assert pass_rate(2, 4) == 0.5
    assert pass_rate(0, 0) == 0.0
