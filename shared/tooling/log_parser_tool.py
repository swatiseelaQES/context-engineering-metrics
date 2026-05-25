import re


def extract_unexpected_status(log: str) -> str | None:
    match = re.search(r"got\s+([a-zA-Z_]+)", log)
    return match.group(1) if match else None
