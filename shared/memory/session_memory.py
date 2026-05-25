class SessionMemory:
    def __init__(self):
        self.items: list[str] = []

    def add(self, item: str) -> None:
        self.items.append(item)

    def recall(self, query: str) -> str:
        query_lower = query.lower()
        matches = [item for item in self.items if any(term in item.lower() for term in query_lower.split())]
        return "\n".join(matches)
