from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import duckdb

from itch_data_pipeline.analytics.lob_snapshots import lob_snapshots_parquet_path
from itch_data_pipeline.analytics.order_events import order_events_parquet_path


PRICE_SCALE = 10_000
DEFAULT_BUCKET_SECONDS = 60


def normalize_price(raw_price: int | float | None, price_scale: int = PRICE_SCALE) -> float | None:
    if raw_price is None:
        return None
    return float(raw_price) / price_scale


def _depth(row: dict[str, Any], side: str, depth: int = 5) -> int:
    return sum(int(row.get(f"{side}_size_{level}") or 0) for level in range(1, depth + 1))


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def liquidity_score(
    *,
    avg_spread_1_raw: float | None,
    avg_total_depth_top5: float | None,
    avg_level1_imbalance: float | None,
    two_sided_snapshot_percent: float | None,
) -> float:
    score = 100.0
    score -= min(float(avg_spread_1_raw or 0) / 20.0, 35.0)
    score += min(float(avg_total_depth_top5 or 0) / 50_000.0 * 20.0, 20.0)
    score -= min(abs(float(avg_level1_imbalance or 0)) * 20.0, 20.0)
    score -= max(0.0, 100.0 - float(two_sided_snapshot_percent or 0)) * 2.0
    return round(max(0.0, min(100.0, score)), 2)


def stress_regime(score: float, avg_spread_1_raw: float | None, two_sided_snapshot_percent: float | None) -> str:
    if score < 55 or float(two_sided_snapshot_percent or 0) < 95:
        return "stressed"
    if score < 75 or float(avg_spread_1_raw or 0) > 500:
        return "watch"
    return "stable"


def build_liquidity_bars_from_snapshots(
    rows: list[dict[str, Any]],
    order_event_rows: list[dict[str, Any]] | None = None,
    *,
    bucket_seconds: int = DEFAULT_BUCKET_SECONDS,
    price_scale: int = PRICE_SCALE,
) -> list[dict[str, Any]]:
    bucket_ns = bucket_seconds * 1_000_000_000
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        symbol = str(row["symbol"]).upper()
        bucket_start_ns = int(row["timestamp_ns"]) // bucket_ns * bucket_ns
        groups[(symbol, bucket_start_ns)].append(row)

    bars: list[dict[str, Any]] = []
    for (symbol, bucket_start_ns), group in sorted(groups.items()):
        snapshot_count = len(group)
        two_sided = [
            row
            for row in group
            if row.get("bid_price_1_raw") is not None and row.get("ask_price_1_raw") is not None
        ]
        spreads = [float(row["spread_1_raw"]) for row in group if row.get("spread_1_raw") is not None]
        mids = [float(row["mid_price_1_raw"]) for row in group if row.get("mid_price_1_raw") is not None]
        imbalances = [
            float(row["level1_imbalance"])
            for row in group
            if row.get("level1_imbalance") is not None
        ]
        bid_depths = [_depth(row, "bid") for row in group]
        ask_depths = [_depth(row, "ask") for row in group]
        avg_spread = sum(spreads) / len(spreads) if spreads else None
        avg_mid = sum(mids) / len(mids) if mids else None
        avg_imbalance = sum(imbalances) / len(imbalances) if imbalances else None
        avg_bid_depth = sum(bid_depths) / snapshot_count
        avg_ask_depth = sum(ask_depths) / snapshot_count
        avg_total_depth = avg_bid_depth + avg_ask_depth
        two_sided_percent = len(two_sided) / snapshot_count * 100
        score = liquidity_score(
            avg_spread_1_raw=avg_spread,
            avg_total_depth_top5=avg_total_depth,
            avg_level1_imbalance=avg_imbalance,
            two_sided_snapshot_percent=two_sided_percent,
        )
        counts = _event_counts_from_rows(
            order_event_rows or [],
            symbol=symbol,
            bucket_start_ns=bucket_start_ns,
            bucket_ns=bucket_ns,
        )
        add_count = int(counts.get("add", 0))
        cancel_count = int(counts.get("cancel", 0))
        execute_count = int(counts.get("execute", 0))
        regime = stress_regime(score, avg_spread, two_sided_percent)

        bars.append(
            {
                "symbol": symbol,
                "bucket_start_ns": bucket_start_ns,
                "bucket_seconds": bucket_seconds,
                "snapshot_count": snapshot_count,
                "two_sided_snapshot_percent": round(two_sided_percent, 4),
                "avg_spread_1_raw": avg_spread,
                "avg_spread_1_display": normalize_price(avg_spread, price_scale),
                "avg_mid_price_1_raw": avg_mid,
                "avg_mid_price_1_display": normalize_price(avg_mid, price_scale),
                "avg_bid_depth_top5": round(avg_bid_depth, 2),
                "avg_ask_depth_top5": round(avg_ask_depth, 2),
                "avg_total_depth_top5": round(avg_total_depth, 2),
                "avg_level1_imbalance": avg_imbalance,
                "event_count": int(sum(counts.values())),
                "add_count": add_count,
                "cancel_count": cancel_count,
                "delete_count": int(counts.get("delete", 0)),
                "execute_count": execute_count,
                "replace_count": int(counts.get("replace", 0)),
                "cancel_to_add_ratio": _safe_ratio(cancel_count, add_count),
                "execute_to_add_ratio": _safe_ratio(execute_count, add_count),
                "liquidity_score": score,
                "stress_regime": regime,
                "stress_label": regime,
            }
        )

    return bars


def _fetch_dicts(query: str, params: list[Any]) -> list[dict[str, Any]]:
    with duckdb.connect(database=":memory:") as conn:
        relation = conn.execute(query, params)
        rows = relation.fetchall()
        columns = [column[0] for column in relation.description]
        return [dict(zip(columns, row)) for row in rows]


def _event_counts_from_rows(
    rows: list[dict[str, Any]],
    *,
    symbol: str,
    bucket_start_ns: int,
    bucket_ns: int,
) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        row_symbol = str(row.get("stock") or row.get("symbol") or "").upper()
        if row_symbol and row_symbol != symbol:
            continue
        timestamp_ns = row.get("timestamp_ns")
        if timestamp_ns is None:
            continue
        row_bucket = int(timestamp_ns) // bucket_ns * bucket_ns
        if row_bucket != bucket_start_ns:
            continue
        event_type = str(row.get("event_type") or "").lower()
        if event_type:
            counts[event_type] += 1
    return counts


def query_liquidity_bars(
    output_root: str | Path,
    *,
    date: str,
    symbol: str,
    bucket_seconds: int = DEFAULT_BUCKET_SECONDS,
    price_scale: int = PRICE_SCALE,
) -> list[dict[str, Any]]:
    symbol = symbol.upper()
    parquet_path = lob_snapshots_parquet_path(output_root, date, symbol)
    if not parquet_path.exists():
        raise FileNotFoundError(f"lob_snapshots Parquet not found: {parquet_path}")

    bucket_ns = bucket_seconds * 1_000_000_000
    rows = _fetch_dicts(
        """
        SELECT
            symbol,
            FLOOR(timestamp_ns / ?)::BIGINT * ?::BIGINT AS bucket_start_ns,
            COUNT(*)::BIGINT AS snapshot_count,
            SUM(CASE WHEN bid_price_1_raw IS NOT NULL AND ask_price_1_raw IS NOT NULL THEN 1 ELSE 0 END)::BIGINT AS two_sided_count,
            AVG(spread_1_raw) AS avg_spread_1_raw,
            AVG(mid_price_1_raw) AS avg_mid_price_1_raw,
            AVG(level1_imbalance) AS avg_level1_imbalance,
            AVG(
                COALESCE(bid_size_1, 0) + COALESCE(bid_size_2, 0) + COALESCE(bid_size_3, 0) +
                COALESCE(bid_size_4, 0) + COALESCE(bid_size_5, 0)
            ) AS avg_bid_depth_top5,
            AVG(
                COALESCE(ask_size_1, 0) + COALESCE(ask_size_2, 0) + COALESCE(ask_size_3, 0) +
                COALESCE(ask_size_4, 0) + COALESCE(ask_size_5, 0)
            ) AS avg_ask_depth_top5
        FROM read_parquet(?)
        GROUP BY symbol, bucket_start_ns
        ORDER BY bucket_start_ns
        """,
        [bucket_ns, bucket_ns, str(parquet_path)],
    )

    event_counts = _order_event_counts_by_bucket(output_root, date=date, symbol=symbol, bucket_ns=bucket_ns)
    bars: list[dict[str, Any]] = []
    for row in rows:
        snapshot_count = int(row["snapshot_count"])
        two_sided_percent = int(row["two_sided_count"]) / snapshot_count * 100 if snapshot_count else 0.0
        avg_bid_depth = float(row["avg_bid_depth_top5"] or 0)
        avg_ask_depth = float(row["avg_ask_depth_top5"] or 0)
        avg_total_depth = avg_bid_depth + avg_ask_depth
        counts = event_counts.get(int(row["bucket_start_ns"]), {})
        add_count = int(counts.get("add", 0))
        cancel_count = int(counts.get("cancel", 0))
        execute_count = int(counts.get("execute", 0))
        score = liquidity_score(
            avg_spread_1_raw=row["avg_spread_1_raw"],
            avg_total_depth_top5=avg_total_depth,
            avg_level1_imbalance=row["avg_level1_imbalance"],
            two_sided_snapshot_percent=two_sided_percent,
        )
        bars.append(
            {
                "symbol": symbol,
                "bucket_start_ns": int(row["bucket_start_ns"]),
                "bucket_seconds": bucket_seconds,
                "snapshot_count": snapshot_count,
                "two_sided_snapshot_percent": round(two_sided_percent, 4),
                "avg_spread_1_raw": float(row["avg_spread_1_raw"]) if row["avg_spread_1_raw"] is not None else None,
                "avg_spread_1_display": normalize_price(row["avg_spread_1_raw"], price_scale),
                "avg_mid_price_1_raw": float(row["avg_mid_price_1_raw"]) if row["avg_mid_price_1_raw"] is not None else None,
                "avg_mid_price_1_display": normalize_price(row["avg_mid_price_1_raw"], price_scale),
                "avg_bid_depth_top5": round(avg_bid_depth, 2),
                "avg_ask_depth_top5": round(avg_ask_depth, 2),
                "avg_total_depth_top5": round(avg_total_depth, 2),
                "avg_level1_imbalance": float(row["avg_level1_imbalance"])
                if row["avg_level1_imbalance"] is not None
                else None,
                "event_count": int(sum(counts.values())),
                "add_count": add_count,
                "cancel_count": cancel_count,
                "delete_count": int(counts.get("delete", 0)),
                "execute_count": execute_count,
                "replace_count": int(counts.get("replace", 0)),
                "cancel_to_add_ratio": _safe_ratio(cancel_count, add_count),
                "execute_to_add_ratio": _safe_ratio(execute_count, add_count),
                "liquidity_score": score,
                "stress_regime": stress_regime(score, row["avg_spread_1_raw"], two_sided_percent),
                "stress_label": stress_regime(score, row["avg_spread_1_raw"], two_sided_percent),
            }
        )

    return bars


def _order_event_counts_by_bucket(
    output_root: str | Path,
    *,
    date: str,
    symbol: str,
    bucket_ns: int,
) -> dict[int, dict[str, int]]:
    parquet_path = order_events_parquet_path(output_root, date, "ALL")
    if not parquet_path.exists():
        return {}

    rows = _fetch_dicts(
        """
        SELECT
            FLOOR(timestamp_ns / ?)::BIGINT * ?::BIGINT AS bucket_start_ns,
            event_type,
            COUNT(*)::BIGINT AS row_count
        FROM read_parquet(?)
        WHERE stock = ?
        GROUP BY bucket_start_ns, event_type
        """,
        [bucket_ns, bucket_ns, str(parquet_path), symbol],
    )
    counts: dict[int, dict[str, int]] = defaultdict(dict)
    for row in rows:
        counts[int(row["bucket_start_ns"])][str(row["event_type"])] = int(row["row_count"])
    return counts


def latest_execution_snapshots(
    output_root: str | Path,
    *,
    date: str,
    symbol: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    symbol = symbol.upper()
    parquet_path = lob_snapshots_parquet_path(output_root, date, symbol)
    if not parquet_path.exists():
        raise FileNotFoundError(f"lob_snapshots Parquet not found: {parquet_path}")

    columns = [
        "snapshot_number",
        "sequence_number",
        "timestamp_ns",
        "symbol",
        "bid_price_1_raw",
        "bid_size_1",
        "bid_price_2_raw",
        "bid_size_2",
        "bid_price_3_raw",
        "bid_size_3",
        "bid_price_4_raw",
        "bid_size_4",
        "bid_price_5_raw",
        "bid_size_5",
        "ask_price_1_raw",
        "ask_size_1",
        "ask_price_2_raw",
        "ask_size_2",
        "ask_price_3_raw",
        "ask_size_3",
        "ask_price_4_raw",
        "ask_size_4",
        "ask_price_5_raw",
        "ask_size_5",
        "spread_1_raw",
        "mid_price_1_raw",
        "level1_imbalance",
    ]
    rows = _fetch_dicts(
        f"""
        SELECT {", ".join(columns)}
        FROM read_parquet(?)
        WHERE bid_price_1_raw IS NOT NULL AND ask_price_1_raw IS NOT NULL
        ORDER BY timestamp_ns DESC
        LIMIT {int(limit)}
        """,
        [str(parquet_path)],
    )
    return sorted(rows, key=lambda row: int(row["timestamp_ns"]))


def simulate_visible_book_cost(
    snapshot: dict[str, Any],
    *,
    side: str,
    order_size: int,
    urgency: str = "normal",
    price_scale: int = PRICE_SCALE,
) -> dict[str, Any]:
    if order_size <= 0:
        raise ValueError("order_size must be positive")

    side = side.lower()
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")
    if urgency not in {"passive", "normal", "aggressive"}:
        raise ValueError("urgency must be passive, normal, or aggressive")

    book_side = "ask" if side == "buy" else "bid"
    levels = [
        {
            "level": level,
            "price_raw": snapshot.get(f"{book_side}_price_{level}_raw"),
            "size": int(snapshot.get(f"{book_side}_size_{level}") or 0),
        }
        for level in range(1, 6)
    ]
    visible_depth = sum(level["size"] for level in levels if level["price_raw"] is not None)

    remaining = int(order_size)
    filled = 0
    notional_raw = 0.0
    consumed_levels = []
    for level in levels:
        if remaining <= 0 or level["price_raw"] is None or level["size"] <= 0:
            continue
        take = min(remaining, level["size"])
        remaining -= take
        filled += take
        notional_raw += take * float(level["price_raw"])
        consumed_levels.append({**level, "shares_taken": take})

    weighted_avg_raw = notional_raw / filled if filled else None
    mid_raw = snapshot.get("mid_price_1_raw")
    if mid_raw is None and snapshot.get("bid_price_1_raw") is not None and snapshot.get("ask_price_1_raw") is not None:
        mid_raw = (float(snapshot["bid_price_1_raw"]) + float(snapshot["ask_price_1_raw"])) / 2

    if weighted_avg_raw is not None and mid_raw:
        slippage_raw = weighted_avg_raw - float(mid_raw) if side == "buy" else float(mid_raw) - weighted_avg_raw
        spread_cost_bps = slippage_raw / float(mid_raw) * 10_000
    else:
        slippage_raw = None
        spread_cost_bps = None

    depth_consumed_percent = filled / visible_depth * 100 if visible_depth else 0.0
    insufficient = filled < order_size
    risk_label = _execution_risk_label(
        insufficient=insufficient,
        depth_consumed_percent=depth_consumed_percent,
        spread_cost_bps=spread_cost_bps,
        urgency=urgency,
    )

    return {
        "symbol": snapshot.get("symbol"),
        "timestamp_ns": snapshot.get("timestamp_ns"),
        "side": side,
        "urgency": urgency,
        "requested_shares": order_size,
        "visible_depth": visible_depth,
        "estimated_fillable_quantity": filled,
        "estimated_unfilled_quantity": order_size - filled,
        "estimated_weighted_avg_price_raw": weighted_avg_raw,
        "estimated_weighted_avg_price_display": normalize_price(weighted_avg_raw, price_scale),
        "mid_price_raw": float(mid_raw) if mid_raw is not None else None,
        "mid_price_display": normalize_price(mid_raw, price_scale),
        "slippage_raw": slippage_raw,
        "spread_cost_bps": spread_cost_bps,
        "depth_consumed_percent": round(depth_consumed_percent, 4),
        "insufficient_visible_liquidity": insufficient,
        "risk_label": risk_label,
        "consumed_levels": consumed_levels,
        "limitation": "Visible top-5 book estimate only; not market impact, alpha, or trading advice.",
    }


def _execution_risk_label(
    *,
    insufficient: bool,
    depth_consumed_percent: float,
    spread_cost_bps: float | None,
    urgency: str,
) -> str:
    if insufficient:
        return "high"
    bps = float(spread_cost_bps or 0)
    depth = depth_consumed_percent
    if urgency == "aggressive":
        high_depth, medium_depth = 70, 35
        high_bps, medium_bps = 8, 3
    elif urgency == "passive":
        high_depth, medium_depth = 90, 55
        high_bps, medium_bps = 15, 6
    else:
        high_depth, medium_depth = 80, 45
        high_bps, medium_bps = 10, 4

    if depth >= high_depth or bps >= high_bps:
        return "high"
    if depth >= medium_depth or bps >= medium_bps:
        return "medium"
    return "low"


def demo_data_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data_fixtures" / "liquidityiq_demo.json"


def load_liquidityiq_demo(path: str | Path | None = None) -> dict[str, Any]:
    demo_path = Path(path) if path is not None else demo_data_path()
    with demo_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def liquidityiq_from_artifacts(
    output_root: str | Path,
    *,
    date: str,
    symbols: list[str],
    bucket_seconds: int = DEFAULT_BUCKET_SECONDS,
) -> dict[str, Any]:
    bars: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    missing: list[str] = []
    for symbol in symbols:
        try:
            bars.extend(
                query_liquidity_bars(
                    output_root,
                    date=date,
                    symbol=symbol,
                    bucket_seconds=bucket_seconds,
                )
            )
            snapshots.extend(latest_execution_snapshots(output_root, date=date, symbol=symbol, limit=20))
        except FileNotFoundError as exc:
            missing.append(str(exc))

    return {
        "metadata": {
            "mode": "local_artifacts",
            "date": date,
            "symbols": [symbol.upper() for symbol in symbols],
            "bucket_seconds": bucket_seconds,
            "price_scale": PRICE_SCALE,
            "missing": missing,
        },
        "liquidity_buckets": bars,
        "execution_snapshots": snapshots,
        "evidence": {
            "source": "local private artifacts",
            "limitations": [
                "No extraction is triggered by LiquidityIQ.",
                "Visible top-5 book analytics are not full market impact or trading advice.",
            ],
        },
    }
