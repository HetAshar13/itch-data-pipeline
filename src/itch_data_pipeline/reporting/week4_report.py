from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from itch_data_pipeline.analytics.message_events import message_type_counts
from itch_data_pipeline.manifests.manifest_writer import read_manifest
from itch_data_pipeline.utils.paths import partition_path


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_week4_showcase_report(
    output_root: str | Path = "outputs/local",
    date: str = "2019-12-30",
    symbol: str = "ALL",
    report_path: str | Path = "reports/week4_showcase.md",
    top_n: int = 10,
) -> dict[str, Any]:
    partition_dir = partition_path(output_root, "message_events", date, symbol)
    parquet_path = partition_dir / "part-000.parquet"
    manifest_path = partition_dir / "manifest.json"
    validation_path = partition_dir / "validation_report.json"
    report = Path(report_path)

    manifest = read_manifest(manifest_path)
    validation = _read_json(validation_path)
    top_message_types = message_type_counts(output_root, date=date, symbol=symbol, limit=top_n)

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _render_markdown(
            date=date,
            symbol=symbol,
            parquet_path=parquet_path,
            manifest=manifest,
            manifest_path=manifest_path,
            validation=validation,
            validation_path=validation_path,
            top_message_types=top_message_types,
        ),
        encoding="utf-8",
    )

    return {
        "report_path": str(report),
        "parquet_path": str(parquet_path),
        "manifest_path": str(manifest_path),
        "validation_report_path": str(validation_path),
        "row_count": manifest["row_counts"]["message_events"],
        "validation_status": validation["status"],
    }


def _render_markdown(
    date: str,
    symbol: str,
    parquet_path: Path,
    manifest: dict[str, Any],
    manifest_path: Path,
    validation: dict[str, Any],
    validation_path: Path,
    top_message_types: list[dict[str, Any]],
) -> str:
    rows = "\n".join(
        f"| {row['message_type']} | {row['message_class']} | {row['row_count']} |"
        for row in top_message_types
    )
    return f"""# Message Event Showcase Report

## Summary

This report demonstrates a bounded, reproducible data engineering path over a real Nasdaq BX ITCH sample file.

## Input And Run Metadata

- Input file: `{manifest["input_file"]}`
- Input SHA-256: `{manifest["input_sha256"]}`
- Date partition: `{date}`
- Symbol partition: `{symbol}`
- Max messages: `{manifest["max_messages"]}`
- Rows written: `{manifest["row_counts"]["message_events"]}`
- Run status: `{manifest["status"]}`
- Validation status: `{validation["status"]}`

## Output Artifacts

- Parquet dataset: `{parquet_path}`
- Manifest: `{manifest_path}`
- Validation report: `{validation_path}`

## Top Message Types

| Message Type | MeatPy Class | Row Count |
| --- | --- | ---: |
{rows}

## What This Proves

- MeatPy can read the real ITCH sample.
- The project can write partitioned Parquet output.
- The manifest records reproducibility metadata.
- Structural validation checks the output shape and row count consistency.
- DuckDB can query the Parquet output directly.
- The Streamlit app exists as a thin presentation layer over these artifacts.

## What This Does Not Prove Yet

- It does not prove full order book correctness.
- It does not run the LOB snapshot pipeline.
- It does not run SLURM jobs.
- It does not make Streamlit responsible for pipeline execution.
"""
