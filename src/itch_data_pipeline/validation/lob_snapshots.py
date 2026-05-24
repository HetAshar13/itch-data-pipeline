from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from itch_data_pipeline.manifests.manifest_writer import read_manifest
from itch_data_pipeline.meatpy_integration.lob_snapshots import LOB_SNAPSHOT_COLUMNS
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


def validate_lob_snapshots_partition(
    output_root: str | Path,
    date: str,
    symbol: str,
) -> dict[str, Any]:
    symbol = symbol.upper()
    out_dir = partition_path(output_root, "lob_snapshots", date, symbol)
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

    missing_columns = [column for column in LOB_SNAPSHOT_COLUMNS if column not in columns]
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
        manifest_count = manifest.get("row_counts", {}).get("lob_snapshots")
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

    if "symbol" in columns:
        symbols = sorted(value for value in frame["symbol"].dropna().unique())
        single_symbol = symbols == [symbol]
        findings.append(
            _finding(
                "single_requested_symbol",
                single_symbol,
                f"All rows contain symbol={symbol}."
                if single_symbol
                else f"Found symbols: {symbols}; expected only {symbol}.",
                violations=0 if single_symbol else 1,
            )
        )
    else:
        findings.append(
            _finding(
                "single_requested_symbol",
                False,
                "Missing symbol column.",
                violations=1,
            )
        )

    if "sequence_number" in columns:
        sequence_increasing = bool(frame["sequence_number"].is_monotonic_increasing)
        findings.append(
            _finding(
                "sequence_numbers_increasing",
                sequence_increasing,
                "Sequence numbers are monotonically increasing."
                if sequence_increasing
                else "Sequence numbers are not monotonically increasing.",
                violations=0 if sequence_increasing else 1,
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

    if "timestamp_ns" in columns:
        timestamps_non_decreasing = bool(frame["timestamp_ns"].is_monotonic_increasing)
        findings.append(
            _finding(
                "timestamps_non_decreasing",
                timestamps_non_decreasing,
                "Timestamps are monotonically non-decreasing."
                if timestamps_non_decreasing
                else "Timestamps move backward.",
                violations=0 if timestamps_non_decreasing else 1,
            )
        )
    else:
        findings.append(
            _finding(
                "timestamps_non_decreasing",
                False,
                "Missing timestamp_ns column.",
                violations=1,
            )
        )

    if {"bid_price_1_raw", "ask_price_1_raw"}.issubset(columns):
        both_sides = frame["bid_price_1_raw"].notna() & frame["ask_price_1_raw"].notna()
        two_sided = frame[both_sides]
        crossed = two_sided[two_sided["bid_price_1_raw"] > two_sided["ask_price_1_raw"]]
        crossed_count = len(crossed)
        findings.append(
            _finding(
                "top_of_book_not_crossed",
                crossed_count == 0,
                "Top of book is not crossed where both sides exist."
                if crossed_count == 0
                else f"Rows with crossed top of book: {crossed_count}.",
                violations=crossed_count,
            )
        )
    else:
        findings.append(
            _finding(
                "top_of_book_not_crossed",
                False,
                "Missing bid_price_1_raw or ask_price_1_raw column.",
                violations=1,
            )
        )

    failed = sum(1 for finding in findings if finding["status"] == "failed")
    report = {
        "dataset": "lob_snapshots",
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
