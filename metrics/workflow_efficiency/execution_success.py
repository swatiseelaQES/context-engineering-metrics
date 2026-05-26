def execution_success_score(result):
    tests_collected = result.get("tests_collected", 0)
    tests_passed = result.get("tests_passed", 0)
    tests_failed = result.get("tests_failed", 0)
    pytest_exit_code = result.get("pytest_exit_code")

    if tests_collected == 0:
        return 0.0

    if pytest_exit_code != 0:
        return 0.0

    if tests_failed > 0:
        return 0.0

    return round(tests_passed / tests_collected, 4)