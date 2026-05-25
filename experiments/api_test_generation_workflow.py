from __future__ import annotations

import json
from dataclasses import asdict

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration_agent.api_test_orchestrator import run_generated_api_tests


if __name__ == "__main__":
    metrics = run_generated_api_tests(root=Path.cwd())
    print(json.dumps(asdict(metrics), indent=2))
