from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from shared.config import Settings, get_settings


class LLMClient(Protocol):
    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        ...


@dataclass
class OpenAITestGenerationClient:
    settings: Settings

    @classmethod
    def from_env(cls) -> "OpenAITestGenerationClient":
        return cls(get_settings())

    def _client(self):
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        # Lazy imports keep local unit tests runnable before dependencies are installed.
        import httpx
        from openai import OpenAI

        # SSL verification is intentionally configurable for this demo.
        # The repo default is false because the user asked for both OpenAI and
        # Restful Booker calls not to require verify=True. In production, prefer true.
        http_client = httpx.Client(verify=self.settings.openai_verify_ssl, timeout=60.0)
        return OpenAI(api_key=self.settings.openai_api_key, http_client=http_client)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        client = self._client()
        response = client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text


class DeterministicFallbackClient:
    """Fallback used when no OPENAI_API_KEY is available.

    The fallback keeps the orchestration runnable in CI and lets the metrics
    pipeline work without sending external requests.
    """

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        from test_generation.templates import RESTFUL_BOOKER_PYTEST_TEMPLATE

        return RESTFUL_BOOKER_PYTEST_TEMPLATE


def get_llm_client(settings: Settings | None = None) -> LLMClient:
    settings = settings or get_settings()
    if settings.openai_api_key:
        return OpenAITestGenerationClient(settings)
    return DeterministicFallbackClient()
