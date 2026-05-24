from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from itch_data_pipeline.manifests.manifest_writer import read_manifest
from itch_data_pipeline.meatpy_integration.order_events import ORDER_EVENT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path


def _finding(
    rule_name: str,
    passed: bool,
    message: str,
    violations: int = 0,
    severity: str = "high",
) -> dict[str, Any]:
    return {
        "rule_name": rule_name,
        "status": "passed" if passed else "failed",
        "severity": severity,
        "violations": violations,
        "message": message,
    }


def _order_ref_violations(frame: pd.DataFrame) -> int:
    if not {"event_type", "order_ref", "original_ref", "new_ref"}.issubset(frame.columns):
        return len(frame)

    replace_missing = frame[
        (frame["event_type"] == "replace")
        & (frame["original_ref"].isna() | frame["new_ref"].isna())
    ]
    other_missing = frame[
        (frame["event_type"] != "replace")
        & frame["order_ref"].isna()
    ]
    return len(replace_missing) + len(other_missing)


def validate_order_events_partition(
    output_root: str | Path,
    date: str,
    symbol: str = "ALL",
) -> dict[str, Any]:
    out_dir = partition_path(output_root, "order_events", date, symbol)
    parquet_path = out_dir / "part-000.parquet"
    manifest_path = out_dir / "manifest.json"
    report_path = out_dir / "validation_report.json"

    findings = []
    if not parquet_path.exists():
        frame = pd.DataFrame()
        row_count = 0
        columns = []
        findings.append(
            _finding(
                "parquet_file_exists",
                False,
                f"Missing Parquet file: {parquet_path}",
                violations=1,
            )
        )
    else:
        frame = pd.read_parquet(parquet_path)
        row_count = len(frame)
        columns = list(frame.columns)
        findings.append(
            _finding(
                "parquet_file_exists",
                True,
                "Parquet file exists.",
            )
        )

    missing_columns = [column for column in ORDER_EVENT_COLUMNS if column not in columns]
    findings.append(
        _finding(
            "expected_columns_present",
            not missing_columns,
            "All expected columns are present."
            if not missing_columns
            else f"Missing columns: {missing_columns}",
            violations=len(missing_columns),
        )
    )

    findings.append(
        _finding(
            "row_count_positive",
            row_count > 0,
            f"Row count is {row_count}.",
            violations=0 if row_count > 0 else 1,
        )
    )

    if manifest_path.exists():
        manifest = read_manifest(manifest_path)
        manifest_count = manifest.get("row_counts", {}).get("order_events")
        count_matches = manifest_count == row_count
        findings.append(
            _finding(
                "manifest_row_count_matches_parquet",
                count_matches,
                f"Manifest count={manifest_count}, Parquet count={row_count}.",
                violations=0 if count_matches else 1,
            )
        )
    else:
        findings.append(
            _finding(
                "manifest_exists",
                False,
                f"Missing manifest file: {manifest_path}",
                violations=1,
            )
        )

    if "event_type" in columns:
        missing_event_type = int(frame["event_type"].isna().sum())
        findings.append(
            _finding(
                "event_type_present",
                missing_event_type == 0,
                "All order event rows have an event_type."
                if missing_event_type == 0
                else f"Rows missing event_type: {missing_event_type}.",
                violations=missing_event_type,
            )
        )
    else:
        findings.append(
            _finding(
                "event_type_present",
                False,
                "Missing event_type column.",
                violations=row_count,
            )
        )

    order_ref_violations = _order_ref_violations(frame)
    findings.append(
        _finding(
            "order_refs_present",
            order_ref_violations == 0,
            "All order event rows have the expected order reference fields."
            if order_ref_violations == 0
            else f"Rows missing expected order reference fields: {order_ref_violations}.",
            violations=order_ref_violations,
        )
    )

    if "sequence_number" in columns:
        increasing = bool(frame["sequence_number"].is_monotonic_increasing)
        findings.append(
            _finding(
                "sequence_numbers_increasing",
                increasing,
                "Sequence numbers are monotonically increasing."
                if increasing
                else "Sequence numbers are not monotonically increasing.",
                violations=0 if increasing else 1,
            )
        )
    else:
        findings.append(
            _finding(
                "sequence_numbers_increasing",
                False,
                "Missing sequence_number column.",
                violations=1,
            )
        )

    failed = sum(1 for finding in findings if finding["status"] == "failed")
    report = {
        "dataset": "order_events",
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
