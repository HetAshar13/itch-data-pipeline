from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from itch_data_pipeline.utils.paths import partition_path


def message_events_parquet_path(
    output_root: str | Path,
    date: str,
    symbol: str = "ALL",
) -> Path:
    return partition_path(output_root, "message_events", date, symbol) / "part-000.parquet"


def message_type_counts(
    output_root: str | Path,
    date: str,
    symbol: str = "ALL",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    parquet_path = message_events_parquet_path(output_root, date, symbol)
    if not parquet_path.exists():
        raise FileNotFoundError(f"message_events Parquet not found: {parquet_path}")

    limit_sql = "" if limit is None else f" LIMIT {int(limit)}"
    query = f"""
        SELECT
            message_type,
            message_class,
            COUNT(*) AS row_count
        FROM read_parquet(?)
        GROUP BY message_type, message_class
        ORDER BY row_count DESC, message_type, message_class
        {limit_sql}
    """
    rows = duckdb.sql(query, params=[str(parquet_path)]).fetchall()
    return [
        {
            "message_type": message_type,
            "message_class": message_class,
            "row_count": int(row_count),
        }
        for message_type, message_class, row_count in rows
    ]
