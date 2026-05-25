from __future__ import annotations

import json
from typing import Any

import tiktoken


DEFAULT_MODEL = "gpt-4o-mini"


def _to_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, (list, tuple, set)):
        return "\n".join(_to_text(item) for item in value)

    if isinstance(value, dict):
        return json.dumps(value, indent=2, sort_keys=True)

    return str(value)


def count_tokens(value: Any, model: str = DEFAULT_MODEL) -> int:
    text = _to_text(value)

    if not text.strip():
        return 0

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def workflow_tokens(
    prompt: Any = None,
    context: Any = None,
    output: Any = None,
    tool_calls: Any = None,
    model: str = DEFAULT_MODEL,
) -> int:
    return (
        count_tokens(prompt, model)
        + count_tokens(context, model)
        + count_tokens(output, model)
        + count_tokens(tool_calls, model)
    )