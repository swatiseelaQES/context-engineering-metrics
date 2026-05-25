from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shared.config import Settings, get_settings
from shared.llm.client import LLMClient, get_llm_client
from test_generation.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


@dataclass
class TestGenerationResult:
    path: Path
    used_openai: bool
    tokens_estimated: int
    context_files: list[str]


def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip() + "\n"
    return text + "\n"


def estimate_tokens(*parts: str) -> int:
    # Rough, deterministic estimate that is good enough for demo metrics.
    return max(1, sum(len(p.split()) for p in parts))


def generate_restful_booker_tests(
    settings: Settings | None = None,
    client: LLMClient | None = None,
    root: Path | None = None,
) -> TestGenerationResult:
    settings = settings or get_settings()
    root = root or Path.cwd()
    client = client or get_llm_client(settings)

    contract_path = root / "datasets" / "api_contracts" / "restful_booker_openapi.yaml"
    strategy_path = root / "datasets" / "api_contracts" / "restful_booker_test_strategy.md"
    contract = contract_path.read_text()
    strategy = strategy_path.read_text()
    user_prompt = USER_PROMPT_TEMPLATE.format(contract=contract, strategy=strategy)

    generated_code = strip_markdown_fences(client.generate_text(SYSTEM_PROMPT, user_prompt))

    output_dir = root / settings.generated_test_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / settings.generated_test_file
    output_path.write_text(generated_code)

    return TestGenerationResult(
        path=output_path,
        used_openai=bool(settings.openai_api_key),
        tokens_estimated=estimate_tokens(SYSTEM_PROMPT, user_prompt, generated_code),
        context_files=[str(contract_path), str(strategy_path)],
    )


if __name__ == "__main__":
    result = generate_restful_booker_tests()
    print(f"Generated: {result.path}")
    print(f"Used OpenAI: {result.used_openai}")
