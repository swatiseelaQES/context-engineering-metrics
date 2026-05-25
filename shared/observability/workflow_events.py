import json
from dataclasses import asdict
from pathlib import Path


def write_trace(result, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    payload = result if isinstance(result, dict) else asdict(result)

    Path(path).write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8"
    )