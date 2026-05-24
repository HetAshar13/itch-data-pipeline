from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from itch_data_pipeline.manifests.manifest_writer import read_manifest
from itch_data_pipeline.meatpy_integration.extract import MESSAGE_EVENT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path


def validate_message_events_partition(
    output_root: str | Path,
    date: str,
    symbol: str = "ALL",
) -> dict[str, Any]:
    out_dir = partition_path(output_root, "message_events", date, symbol)
    parquet_path = out_dir / "part-000.parquet"
    manifest_path = out_dir / "manifest.json"
    report_path = out_dir / "validation_report.json"

    findings = []

    if not parquet_path.exists():
        findings.append(
            {
                "rule_name": "parquet_file_exists",
                "status": "failed",
                "severity": "high",
                "violations": 1,
                "message": f"Missing Parquet file: {parquet_path}",
            }
        )
        row_count = 0
        columns = []
    else:
        frame = pd.read_parquet(parquet_path)
        row_count = len(frame)
        columns = list(frame.columns)
        findings.append(
            {
                "rule_name": "parquet_file_exists",
                "status": "passed",
                "severity": "high",
                "violations": 0,
                "message": "Parquet file exists.",
            }
        )

    missing_columns = [column for column in MESSAGE_EVENT_COLUMNS if column not in columns]
    findings.append(
        {
            "rule_name": "expected_columns_present",
            "status": "passed" if not missing_columns else "failed",
            "severity": "high",
            "violations": len(missing_columns),
            "message": "All expected columns are present."
            if not missing_columns
            else f"Missing columns: {missing_columns}",
        }
    )

    findings.append(
        {
            "rule_name": "row_count_positive",
            "status": "passed" if row_count > 0 else "failed",
            "severity": "high",
            "violations": 0 if row_count > 0 else 1,
            "message": f"Row count is {row_count}.",
        }
    )

    if manifest_path.exists():
        manifest = read_manifest(manifest_path)
        manifest_count = manifest.get("row_counts", {}).get("message_events")
        count_matches = manifest_count == row_count
        findings.append(
            {
                "rule_name": "manifest_row_count_matches_parquet",
                "status": "passed" if count_matches else "failed",
                "severity": "high",
                "violations": 0 if count_matches else 1,
                "message": f"Manifest count={manifest_count}, Parquet count={row_count}.",
            }
        )
    else:
        findings.append(
            {
                "rule_name": "manifest_exists",
                "status": "failed",
                "severity": "high",
                "violations": 1,
                "message": f"Missing manifest file: {manifest_path}",
            }
        )

    failed = sum(1 for finding in findings if finding["status"] == "failed")
    report = {
        "dataset": "message_events",
        "date": date,
        "symbol": symbol,
        "parquet_path": str(parquet_path),
        "manifest_path": str(manifest_path),
        "row_count": row_count,
        "status": "passed" if failed == 0 else "failed",
        "rules_run": len(findings),
        "rules_failed": failed,
        "findings": findings,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    return {
        "validation_report_path": str(report_path),
        "status": report["status"],
        "rules_run": report["rules_run"],
        "rules_failed": report["rules_failed"],
    }
