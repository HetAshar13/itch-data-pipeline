from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from itch_data_pipeline.utils.paths import partition_path


def order_events_parquet_path(
    output_root: str | Path,
    date: str,
    symbol: str = "ALL",
) -> Path:
    return partition_path(output_root, "order_events", date, symbol) / "part-000.parquet"


def _fetch_dicts(query: str, parquet_path: Path) -> list[dict[str, Any]]:
    relation = duckdb.sql(query, params=[str(parquet_path)])
    rows = relation.fetchall()
    columns = [column[0] for column in relation.description]
    return [dict(zip(columns, row)) for row in rows]


def order_event_summary(
    output_root: str | Path,
    date: str,
    symbol: str = "ALL",
    limit: int = 10,
) -> dict[str, Any]:
    parquet_path = order_events_parquet_path(output_root, date, symbol)
    if not parquet_path.exists():
        raise FileNotFoundError(f"order_events Parquet not found: {parquet_path}")

    event_counts = _fetch_dicts(
        f"""
        SELECT event_type, COUNT(*)::BIGINT AS row_count
        FROM read_parquet(?)
        GROUP BY event_type
        ORDER BY row_count DESC, event_type
        LIMIT {int(limit)}
        """,
        parquet_path,
    )
    side_counts = _fetch_dicts(
        """
        SELECT side, COUNT(*)::BIGINT AS row_count, SUM(shares)::BIGINT AS total_shares
        FROM read_parquet(?)
        WHERE event_type = 'add'
        GROUP BY side
        ORDER BY row_count DESC, side
        """,
        parquet_path,
    )
    top_stocks_by_adds = _fetch_dicts(
        f"""
        SELECT stock, COUNT(*)::BIGINT AS add_count, SUM(shares)::BIGINT AS total_add_shares
        FROM read_parquet(?)
        WHERE event_type = 'add' AND stock IS NOT NULL
        GROUP BY stock
        ORDER BY add_count DESC, stock
        LIMIT {int(limit)}
        """,
        parquet_path,
    )
    activity_rows = _fetch_dicts(
        """
        SELECT event_type, COUNT(*)::BIGINT AS row_count
        FROM read_parquet(?)
        GROUP BY event_type
        """,
        parquet_path,
    )

    return {
        "event_counts": [
            {"event_type": row["event_type"], "row_count": int(row["row_count"])}
            for row in event_counts
        ],
        "side_counts": [
            {
                "side": row["side"],
                "row_count": int(row["row_count"]),
                "total_shares": int(row["total_shares"] or 0),
            }
            for row in side_counts
        ],
        "top_stocks_by_adds": [
            {
                "stock": row["stock"],
                "add_count": int(row["add_count"]),
                "total_add_shares": int(row["total_add_shares"] or 0),
            }
            for row in top_stocks_by_adds
        ],
        "activity_counts": {
            row["event_type"]: int(row["row_count"])
            for row in activity_rows
        },
    }
