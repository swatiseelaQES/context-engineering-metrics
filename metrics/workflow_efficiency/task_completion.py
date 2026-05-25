def task_completion_score(output: str, expected_root_cause: str) -> float:
    output_lower = output.lower()
    required_terms = ["settled", "contract", "test"]
    return sum(term in output_lower for term in required_terms) / len(required_terms)
