from __future__ import annotations


def pass_rate(tests_passed: int, tests_collected: int) -> float:
    if tests_collected == 0:
        return 0.0
    return tests_passed / tests_collected


def human_correction_needed(pytest_exit_code: int) -> bool:
    return pytest_exit_code != 0


def generated_test_coverage_score(required_flows: set[str], generated_code: str) -> float:
    if not required_flows:
        return 0.0
    matched = sum(1 for flow in required_flows if flow.lower() in generated_code.lower())
    return matched / len(required_flows)
