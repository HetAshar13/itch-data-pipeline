from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from itch_data_pipeline.analytics.order_events import order_event_summary
from itch_data_pipeline.analytics.message_events import message_type_counts
from itch_data_pipeline.manifests.manifest_writer import read_manifest
from itch_data_pipeline.utils.paths import partition_path


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_showcase_context(
    output_root: str | Path = "outputs/local",
    date: str = "2019-12-30",
    symbol: str = "ALL",
    top_n: int = 10,
    sample_rows: int = 20,
) -> dict[str, Any]:
    partition_dir = partition_path(output_root, "message_events", date, symbol)
    parquet_path = partition_dir / "part-000.parquet"
    manifest_path = partition_dir / "manifest.json"
    validation_path = partition_dir / "validation_report.json"

    manifest = read_manifest(manifest_path)
    validation = _read_json(validation_path)
    top_message_types = message_type_counts(output_root, date=date, symbol=symbol, limit=top_n)
    sample = pd.read_parquet(parquet_path).head(sample_rows)
    order_events = _load_order_events_context(
        output_root=output_root,
        date=date,
        symbol=symbol,
        top_n=top_n,
        sample_rows=sample_rows,
    )

    return {
        "date": date,
        "symbol": symbol,
        "partition_dir": str(partition_dir),
        "parquet_path": str(parquet_path),
        "manifest_path": str(manifest_path),
        "validation_report_path": str(validation_path),
        "manifest": manifest,
        "validation": validation,
        "top_message_types": top_message_types,
        "sample_rows": sample.to_dict(orient="records"),
        "order_events": order_events,
    }


def _load_order_events_context(
    output_root: str | Path,
    date: str,
    symbol: str,
    top_n: int,
    sample_rows: int,
) -> dict[str, Any]:
    partition_dir = partition_path(output_root, "order_events", date, symbol)
    parquet_path = partition_dir / "part-000.parquet"
    manifest_path = partition_dir / "manifest.json"
    validation_path = partition_dir / "validation_report.json"

    if not parquet_path.exists() or not manifest_path.exists() or not validation_path.exists():
        return {
            "available": False,
            "partition_dir": str(partition_dir),
        }

    sample = pd.read_parquet(parquet_path).head(sample_rows)
    return {
        "available": True,
        "partition_dir": str(partition_dir),
        "parquet_path": str(parquet_path),
        "manifest_path": str(manifest_path),
        "validation_report_path": str(validation_path),
        "manifest": read_manifest(manifest_path),
        "validation": _read_json(validation_path),
        "summary": order_event_summary(output_root, date=date, symbol=symbol, limit=top_n),
        "sample_rows": sample.to_dict(orient="records"),
    }
