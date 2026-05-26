def _to_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(_to_text(item) for item in value)

    if isinstance(value, dict):
        return " ".join(f"{k} {v}" for k, v in value.items())

    return str(value)


def _normalize(value):
    return _to_text(value).lower().replace("-", " ")


def task_completion_score(output, success_criteria):
    """
    Measures how well the agent output addresses the task success criteria.

    For API test generation, this means:
    - generated test file
    - pytest collection/execution
    - API execution
    - passing test signal
    """

    output_text = _normalize(output)
    criteria = success_criteria if isinstance(success_criteria, list) else [success_criteria]

    if not output_text.strip() or not criteria:
        return 0.0

    matched = 0

    for criterion in criteria:
        criterion_text = _normalize(criterion)

        keywords = [
            word for word in criterion_text.split()
            if len(word) > 3
        ]

        if not keywords:
            continue

        hits = sum(1 for word in keywords if word in output_text)
        coverage = hits / len(keywords)

        if coverage >= 0.5:
            matched += 1

    return round(matched / len(criteria), 4)