def _to_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(str(item) for item in value)

    return str(value)


def has_unsupported_regression_claim(output, retrieved_context):
    output_lower = _to_text(output).lower()
    context_lower = _to_text(retrieved_context).lower()

    regression_terms = [
        "regression",
        "previously worked",
        "recent change",
        "broke after deployment",
        "new release caused",
    ]

    mentions_regression = any(term in output_lower for term in regression_terms)
    supported_by_context = any(term in context_lower for term in regression_terms)

    return mentions_regression and not supported_by_context