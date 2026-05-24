from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.peek import summarize_itch50_messages
from itch_data_pipeline.meatpy_integration.probe import probe_meatpy
from itch_data_pipeline.utils.hashing import sha256_file
from itch_data_pipeline.utils.logging_utils import get_logger
from itch_data_pipeline.utils.paths import partition_path


def run_sample_peek(
    input_path: str | Path,
    output_root: str | Path = "outputs/local",
    limit: int = 10,
    schema_version: str = "1.0",
) -> dict[str, Any]:
    logger = get_logger(__name__)
    start = datetime.now(timezone.utc)
    input_file = Path(input_path)
    out_dir = partition_path(output_root, "message_peek", "unknown", "ALL")
    summary_path = out_dir / "summary.json"
    manifest_path = out_dir / "manifest.json"

    logger.info("Starting sample peek run for %s with limit=%s", input_file, limit)
    summary = summarize_itch50_messages(input_file, limit=limit)
    out_dir.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    logger.info("Wrote sample peek summary to %s", summary_path)

    meatpy_probe = probe_meatpy()
    end = datetime.now(timezone.utc)
    manifest = {
        "run_id": f"sample_peek_{start.strftime('%Y%m%dT%H%M%S%fZ')}",
        "date": "unknown",
        "symbol": "ALL",
        "input_file": str(input_file),
        "input_sha256": sha256_file(input_file),
        "output_paths": [str(summary_path)],
        "schema_version": schema_version,
        "meatpy_version": str(meatpy_probe.get("version", "unknown")),
        "meatpy_probe": meatpy_probe,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "duration_seconds": (end - start).total_seconds(),
        "status": "success",
        "row_counts": {"messages_read": summary["messages_read"]},
        "validation_summary": {
            "rules_run": 0,
            "rules_failed": 0,
            "status": "not_run",
        },
    }
    write_manifest(manifest, manifest_path)
    logger.info("Wrote sample peek manifest to %s", manifest_path)

    return {
        "summary_path": str(summary_path),
        "manifest_path": str(manifest_path),
        "messages_read": summary["messages_read"],
    }
