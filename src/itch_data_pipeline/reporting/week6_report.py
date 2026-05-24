from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from itch_data_pipeline.analytics.message_events import message_type_counts
from itch_data_pipeline.analytics.order_events import order_event_summary
from itch_data_pipeline.manifests.manifest_writer import read_manifest
from itch_data_pipeline.utils.paths import partition_path


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_week6_showcase_report(
    output_root: str | Path = "outputs/local",
    date: str = "2019-12-30",
    symbol: str = "ALL",
    report_path: str | Path = "reports/week6_showcase.md",
    top_n: int = 10,
) -> dict[str, Any]:
    message_dir = partition_path(output_root, "message_events", date, symbol)
    order_dir = partition_path(output_root, "order_events", date, symbol)
    message_manifest_path = message_dir / "manifest.json"
    message_validation_path = message_dir / "validation_report.json"
    order_manifest_path = order_dir / "manifest.json"
    order_validation_path = order_dir / "validation_report.json"
    report = Path(report_path)

    message_manifest = read_manifest(message_manifest_path)
    message_validation = _read_json(message_validation_path)
    order_manifest = read_manifest(order_manifest_path)
    order_validation = _read_json(order_validation_path)
    top_message_types = message_type_counts(output_root, date=date, symbol=symbol, limit=top_n)
    order_summary = order_event_summary(output_root, date=date, symbol=symbol, limit=top_n)

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _render_markdown(
            date=date,
            symbol=symbol,
            message_manifest=message_manifest,
            message_validation=message_validation,
            message_manifest_path=message_manifest_path,
            message_validation_path=message_validation_path,
            order_manifest=order_manifest,
            order_validation=order_validation,
            order_manifest_path=order_manifest_path,
            order_validation_path=order_validation_path,
            top_message_types=top_message_types,
            order_summary=order_summary,
            message_parquet_path=message_dir / "part-000.parquet",
            order_parquet_path=order_dir / "part-000.parquet",
        ),
        encoding="utf-8",
    )

    return {
        "report_path": str(report),
        "message_events_row_count": message_manifest["row_counts"]["message_events"],
        "message_events_validation_status": message_validation["status"],
        "order_events_row_count": order_manifest["row_counts"]["order_events"],
        "order_events_validation_status": order_validation["status"],
    }


def _markdown_rows(rows: list[dict[str, Any]], columns: list[str]) -> str:
    return "\n".join(
        "| " + " | ".join(str(row.get(column, "")) for column in columns) + " |"
        for row in rows
    )


def _render_markdown(
    date: str,
    symbol: str,
    message_manifest: dict[str, Any],
    message_validation: dict[str, Any],
    message_manifest_path: Path,
    message_validation_path: Path,
    order_manifest: dict[str, Any],
    order_validation: dict[str, Any],
    order_manifest_path: Path,
    order_validation_path: Path,
    top_message_types: list[dict[str, Any]],
    order_summary: dict[str, Any],
    message_parquet_path: Path,
    order_parquet_path: Path,
) -> str:
    message_rows = _markdown_rows(top_message_types, ["message_type", "message_class", "row_count"])
    order_rows = _markdown_rows(order_summary["event_counts"], ["event_type", "row_count"])
    side_rows = _markdown_rows(order_summary["side_counts"], ["side", "row_count", "total_shares"])
    stock_rows = _markdown_rows(order_summary["top_stocks_by_adds"], ["stock", "add_count", "total_add_shares"])

    return f"""# Week 6 Showcase Report

## Summary

This report extends the Week 4 pipeline from generic ITCH message events to a bounded order-event dataset. It still uses MeatPy for ITCH message reading and keeps Streamlit as a presentation layer over generated artifacts.

## Run Metadata

- Input file: `{message_manifest["input_file"]}`
- Input SHA-256: `{message_manifest["input_sha256"]}`
- Date partition: `{date}`
- Symbol partition: `{symbol}`
- Message scan bound: `{order_manifest["max_messages"]}`
- `message_events` rows: `{message_manifest["row_counts"]["message_events"]}`
- `order_events` rows: `{order_manifest["row_counts"]["order_events"]}`
- `message_events` validation: `{message_validation["status"]}`
- `order_events` validation: `{order_validation["status"]}`

## Output Artifacts

- `message_events` Parquet: `{message_parquet_path}`
- `message_events` manifest: `{message_manifest_path}`
- `message_events` validation: `{message_validation_path}`
- `order_events` Parquet: `{order_parquet_path}`
- `order_events` manifest: `{order_manifest_path}`
- `order_events` validation: `{order_validation_path}`

## Top Message Types

| Message Type | MeatPy Class | Row Count |
| --- | --- | ---: |
{message_rows}

## Order Event Counts

| Event Type | Row Count |
| --- | ---: |
{order_rows}

## Add Order Side Counts

| Side | Row Count | Total Shares |
| --- | ---: | ---: |
{side_rows}

## Top Stocks By Add Events

| Stock | Add Count | Total Add Shares |
| --- | ---: | ---: |
{stock_rows}

## What This Proves

- MeatPy can read the real ITCH sample without a custom parser.
- The project can derive a second, order-event-focused Parquet dataset.
- Both datasets have manifests and structural validation reports.
- DuckDB can query message-level and order-event-level outputs directly.
- Streamlit can present Week 6 artifacts without running pipeline logic.

## What This Does Not Prove Yet

- It does not reconstruct the full order book.
- It does not prove market microstructure correctness.
- It does not normalize raw ITCH price integers into display prices.
- It does not add Spark, Airflow, Kafka, Snowflake, or ML.
"""
