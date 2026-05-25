from __future__ import annotations

import os
from dataclasses import dataclass


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_verify_ssl: bool = env_bool("OPENAI_VERIFY_SSL", False)

    restful_booker_base_url: str = os.getenv(
        "RESTFUL_BOOKER_BASE_URL", "https://restful-booker.herokuapp.com"
    ).rstrip("/")
    restful_booker_verify_ssl: bool = env_bool("RESTFUL_BOOKER_VERIFY_SSL", False)
    restful_booker_username: str = os.getenv("RESTFUL_BOOKER_USERNAME", "admin")
    restful_booker_password: str = os.getenv("RESTFUL_BOOKER_PASSWORD", "password123")

    generated_test_dir: str = os.getenv("GENERATED_TEST_DIR", "generated_tests")
    generated_test_file: str = os.getenv("GENERATED_TEST_FILE", "test_restful_booker_generated.py")


def get_settings() -> Settings:
    return Settings()
