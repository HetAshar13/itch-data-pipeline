from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_sample_manifest() -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "run_id": "sample_run_001",
        "date": "2019-05-30",
        "symbol": "AAPL",
        "input_file": "sample_data/20190530.BX_ITCH_50.gz",
        "output_paths": [],
        "schema_version": "1.0",
        "meatpy_version": "unknown",
        "start_time": now,
        "end_time": now,
        "duration_seconds": 0,
        "status": "sample",
        "row_counts": {},
        "validation_summary": {
            "rules_run": 0,
            "rules_failed": 0,
            "status": "not_run",
        },
    }


def write_manifest(manifest: dict[str, Any], output_path: str | Path) -> None:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)


def read_manifest(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
