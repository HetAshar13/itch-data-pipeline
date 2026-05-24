from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from itch_data_pipeline.utils.paths import partition_path


def lob_snapshots_parquet_path(
    output_root: str | Path,
    date: str,
    symbol: str,
) -> Path:
    return partition_path(output_root, "lob_snapshots", date, symbol.upper()) / "part-000.parquet"


def lob_snapshot_summary(
    output_root: str | Path,
    date: str,
    symbol: str,
) -> dict[str, Any]:
    symbol = symbol.upper()
    parquet_path = lob_snapshots_parquet_path(output_root, date, symbol)
    if not parquet_path.exists():
        raise FileNotFoundError(f"lob_snapshots Parquet not found: {parquet_path}")

    row = duckdb.sql(
        """
        SELECT
            COUNT(*)::BIGINT AS snapshot_count,
            MIN(timestamp_ns)::BIGINT AS first_timestamp_ns,
            MAX(timestamp_ns)::BIGINT AS last_timestamp_ns,
            SUM(
                CASE
                    WHEN bid_price_1_raw IS NOT NULL AND ask_price_1_raw IS NOT NULL
                    THEN 1 ELSE 0
                END
            )::BIGINT AS two_sided_snapshot_count,
            AVG(spread_1_raw) AS avg_spread_1_raw,
            MEDIAN(spread_1_raw) AS median_spread_1_raw,
            MIN(spread_1_raw) AS min_spread_1_raw,
            MAX(spread_1_raw) AS max_spread_1_raw,
            AVG(level1_imbalance) AS avg_level1_imbalance
        FROM read_parquet(?)
        """,
        params=[str(parquet_path)],
    ).fetchone()

    snapshot_count = int(row[0])
    two_sided_count = int(row[3])
    two_sided_percent = (two_sided_count / snapshot_count * 100) if snapshot_count else 0.0

    return {
        "symbol": symbol,
        "snapshot_count": snapshot_count,
        "first_timestamp_ns": int(row[1]) if row[1] is not None else None,
        "last_timestamp_ns": int(row[2]) if row[2] is not None else None,
        "two_sided_snapshot_count": two_sided_count,
        "two_sided_snapshot_percent": float(two_sided_percent),
        "avg_spread_1_raw": float(row[4]) if row[4] is not None else None,
        "median_spread_1_raw": float(row[5]) if row[5] is not None else None,
        "min_spread_1_raw": int(row[6]) if row[6] is not None else None,
        "max_spread_1_raw": int(row[7]) if row[7] is not None else None,
        "avg_level1_imbalance": float(row[8]) if row[8] is not None else None,
    }

