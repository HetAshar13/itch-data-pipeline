from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.extract import (
    MESSAGE_EVENT_COLUMNS,
    extract_message_event_rows,
)
from itch_data_pipeline.meatpy_integration.probe import probe_meatpy
from itch_data_pipeline.utils.hashing import sha256_file
from itch_data_pipeline.utils.logging_utils import get_logger
from itch_data_pipeline.utils.paths import partition_path


def run_extract_itch50_sample(
    input_path: str | Path,
    date: str,
    output_root: str | Path = "outputs/local",
    max_messages: int = 100_000,
    schema_version: str = "1.0",
) -> dict[str, Any]:
    logger = get_logger(__name__)
    start = datetime.now(timezone.utc)
    input_file = Path(input_path)
    out_dir = partition_path(output_root, "message_events", date, "ALL")
    parquet_path = out_dir / "part-000.parquet"
    manifest_path = out_dir / "manifest.json"

    logger.info(
        "Starting bounded ITCH 5.0 extraction for %s with max_messages=%s",
        input_file,
        max_messages,
    )
    rows = extract_message_event_rows(input_file, max_messages=max_messages)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(rows, columns=MESSAGE_EVENT_COLUMNS)
    frame.to_parquet(parquet_path, index=False)
    logger.info("Wrote message_events Parquet to %s", parquet_path)

    meatpy_probe = probe_meatpy()
    end = datetime.now(timezone.utc)
    manifest = {
        "run_id": f"extract_itch50_sample_{start.strftime('%Y%m%dT%H%M%S%fZ')}",
        "date": date,
        "symbol": "ALL",
        "input_file": str(input_file),
        "input_sha256": sha256_file(input_file),
        "output_paths": [str(parquet_path)],
        "schema_version": schema_version,
        "meatpy_version": str(meatpy_probe.get("version", "unknown")),
        "meatpy_probe": meatpy_probe,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "duration_seconds": (end - start).total_seconds(),
        "status": "success",
        "max_messages": max_messages,
        "row_counts": {"message_events": len(frame)},
        "validation_summary": {
            "rules_run": 0,
            "rules_failed": 0,
            "status": "not_run",
        },
    }
    write_manifest(manifest, manifest_path)
    logger.info("Wrote extraction manifest to %s", manifest_path)

    return {
        "parquet_path": str(parquet_path),
        "manifest_path": str(manifest_path),
        "rows_written": len(frame),
    }
