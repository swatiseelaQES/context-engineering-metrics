def _to_text(value):
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(str(item) for item in value)

    return str(value)


def context_precision(retrieved_context, required_context):
    retrieved_text = _to_text(retrieved_context).lower()
    required_items = required_context if isinstance(required_context, list) else [required_context]

    if not retrieved_text.strip():
        return 0.0

    if not required_items:
        return 0.0

    matched = 0

    for item in required_items:
        item_text = str(item).lower()
        if item_text and item_text in retrieved_text:
            matched += 1

    return matched / len(required_items)