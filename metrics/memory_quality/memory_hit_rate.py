def memory_hit(memory_context: str, expected_terms: list[str]) -> bool:
    return any(term.lower() in memory_context.lower() for term in expected_terms)
