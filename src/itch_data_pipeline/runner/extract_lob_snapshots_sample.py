from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.lob_snapshots import (
    LOB_SNAPSHOT_COLUMNS,
    LOB_SNAPSHOT_DEPTH,
    extract_lob_snapshot_rows_with_metadata,
)
from itch_data_pipeline.meatpy_integration.probe import probe_meatpy
from itch_data_pipeline.utils.hashing import sha256_file
from itch_data_pipeline.utils.logging_utils import get_logger
from itch_data_pipeline.utils.paths import partition_path


def run_extract_lob_snapshots_sample(
    input_path: str | Path,
    date: str,
    symbol: str,
    output_root: str | Path = "outputs/local",
    max_messages: int | None = 1_000_000,
    until_eof: bool = False,
    schema_version: str = "1.0",
) -> dict[str, Any]:
    logger = get_logger(__name__)
    start = datetime.now(timezone.utc)
    input_file = Path(input_path)
    symbol = symbol.upper()
    out_dir = partition_path(output_root, "lob_snapshots", date, symbol)
    parquet_path = out_dir / "part-000.parquet"
    manifest_path = out_dir / "manifest.json"
    scan_limit = None if until_eof else max_messages
    run_mode = "until_eof" if until_eof else "bounded"

    logger.info(
        "Starting %s ITCH 5.0 LOB snapshot extraction for %s symbol=%s max_messages=%s",
        run_mode,
        input_file,
        symbol,
        scan_limit,
    )
    extraction = extract_lob_snapshot_rows_with_metadata(
        input_file,
        date=date,
        symbol=symbol,
        max_messages=scan_limit,
    )
    rows = extraction["rows"]
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.DataFrame(rows, columns=LOB_SNAPSHOT_COLUMNS)
    frame.to_parquet(parquet_path, index=False)
    logger.info("Wrote lob_snapshots Parquet to %s", parquet_path)

    meatpy_probe = probe_meatpy()
    end = datetime.now(timezone.utc)
    manifest = {
        "run_id": f"extract_lob_snapshots_sample_{start.strftime('%Y%m%dT%H%M%S%fZ')}",
        "dataset": "lob_snapshots",
        "date": date,
        "symbol": symbol,
        "input_file": str(input_file),
        "input_sha256": sha256_file(input_file),
        "output_paths": [str(parquet_path)],
        "schema_version": schema_version,
        "snapshot_depth": LOB_SNAPSHOT_DEPTH,
        "meatpy_version": str(meatpy_probe.get("version", "unknown")),
        "meatpy_probe": meatpy_probe,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "duration_seconds": (end - start).total_seconds(),
        "status": "success",
        "run_mode": run_mode,
        "max_messages": scan_limit,
        "until_eof": until_eof,
        "messages_scanned": extraction["messages_scanned"],
        "stop_reason": extraction["stop_reason"],
        "row_counts": {"lob_snapshots": len(frame)},
        "exception_counts": {},
        "validation_summary": {
            "rules_run": 0,
            "rules_failed": 0,
            "status": "not_run",
        },
    }
    write_manifest(manifest, manifest_path)
    logger.info("Wrote lob_snapshots manifest to %s", manifest_path)

    return {
        "parquet_path": str(parquet_path),
        "manifest_path": str(manifest_path),
        "rows_written": len(frame),
        "messages_scanned": extraction["messages_scanned"],
        "stop_reason": extraction["stop_reason"],
    }
