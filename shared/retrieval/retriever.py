from __future__ import annotations

from pathlib import Path


class KeywordRetriever:
    """Tiny keyword retriever for demo purposes.

    This keeps the repo dependency-light while still making retrieval quality measurable.
    """

    def __init__(self, corpus_dirs: list[str]):
        self.documents: list[tuple[str, str]] = []
        for directory in corpus_dirs:
            for path in Path(directory).rglob("*"):
                if path.is_file() and path.suffix in {".md", ".txt", ".json"}:
                    self.documents.append((str(path), path.read_text(encoding="utf-8")))

    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[str, str, int]]:
        query_terms = set(query.lower().replace("`", "").replace(",", " ").split())
        scored = []
        for path, text in self.documents:
            text_terms = set(text.lower().replace("`", "").replace(",", " ").split())
            score = len(query_terms & text_terms)
            if score > 0:
                scored.append((path, text, score))
        return sorted(scored, key=lambda item: item[2], reverse=True)[:top_k]
