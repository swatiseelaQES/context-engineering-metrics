def _to_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(_to_text(item) for item in value)

    if isinstance(value, dict):
        return " ".join(f"{k} {v}" for k, v in value.items())

    return str(value)


def _normalize(text):
    return _to_text(text).lower().replace("-", " ")


def context_precision(retrieved_context, required_context):
    retrieved_text = _normalize(retrieved_context)
    required_items = required_context if isinstance(required_context, list) else [required_context]

    if not retrieved_text.strip() or not required_items:
        return 0.0

    matched = 0

    for item in required_items:
        item_text = _normalize(item)

        # Concept-level matching instead of exact full-sentence matching
        keywords = [
            word for word in item_text.split()
            if len(word) > 3
        ]

        if not keywords:
            continue

        keyword_hits = sum(1 for word in keywords if word in retrieved_text)
        coverage = keyword_hits / len(keywords)

        if coverage >= 0.6:
            matched += 1

    return round(matched / len(required_items), 4)