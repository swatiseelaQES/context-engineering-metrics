def build_context(*parts: str) -> str:
    return "\n\n".join(part for part in parts if part.strip())
