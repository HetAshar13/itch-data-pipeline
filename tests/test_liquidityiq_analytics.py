from __future__ import annotations

from itch_data_pipeline.analytics.liquidityiq import (
    build_liquidity_bars_from_snapshots,
    liquidity_score,
    load_liquidityiq_demo,
    normalize_price,
    simulate_visible_book_cost,
)


def _snapshot(**overrides):
    row = {
        "snapshot_number": 1,
        "sequence_number": 10,
        "timestamp_ns": 60_000_000_000,
        "symbol": "SPY",
        "bid_price_1_raw": 100_000,
        "bid_size_1": 100,
        "bid_price_2_raw": 99_900,
        "bid_size_2": 200,
        "bid_price_3_raw": 99_800,
        "bid_size_3": 300,
        "bid_price_4_raw": 99_700,
        "bid_size_4": 400,
        "bid_price_5_raw": 99_600,
        "bid_size_5": 500,
        "ask_price_1_raw": 100_200,
        "ask_size_1": 100,
        "ask_price_2_raw": 100_300,
        "ask_size_2": 200,
        "ask_price_3_raw": 100_400,
        "ask_size_3": 300,
        "ask_price_4_raw": 100_500,
        "ask_size_4": 400,
        "ask_price_5_raw": 100_600,
        "ask_size_5": 500,
        "spread_1_raw": 200,
        "mid_price_1_raw": 100_100,
        "level1_imbalance": 0.0,
    }
    row.update(overrides)
    return row


def test_normalize_price_keeps_raw_units_separate():
    assert normalize_price(1_234_500) == 123.45
    assert normalize_price(None) is None


def test_build_liquidity_bars_combines_lob_and_order_event_counts():
    rows = [_snapshot(), _snapshot(snapshot_number=2, timestamp_ns=80_000_000_000, spread_1_raw=400)]
    events = [
        {"timestamp_ns": 61_000_000_000, "stock": "SPY", "event_type": "add"},
        {"timestamp_ns": 62_000_000_000, "stock": "SPY", "event_type": "cancel"},
        {"timestamp_ns": 63_000_000_000, "stock": "QQQ", "event_type": "add"},
    ]

    bars = build_liquidity_bars_from_snapshots(rows, events)

    assert len(bars) == 1
    bar = bars[0]
    assert bar["symbol"] == "SPY"
    assert bar["snapshot_count"] == 2
    assert bar["avg_spread_1_raw"] == 300
    assert bar["avg_spread_1_display"] == 0.03
    assert bar["avg_bid_depth_top5"] == 1500
    assert bar["avg_ask_depth_top5"] == 1500
    assert bar["event_count"] == 2
    assert bar["add_count"] == 1
    assert bar["cancel_count"] == 1
    assert bar["cancel_to_add_ratio"] == 1
    assert bar["stress_label"] in {"stable", "watch", "stressed"}


def test_liquidity_score_penalizes_wide_spreads_and_weak_coverage():
    strong = liquidity_score(
        avg_spread_1_raw=100,
        avg_total_depth_top5=100_000,
        avg_level1_imbalance=0.05,
        two_sided_snapshot_percent=100,
    )
    weak = liquidity_score(
        avg_spread_1_raw=900,
        avg_total_depth_top5=500,
        avg_level1_imbalance=0.9,
        two_sided_snapshot_percent=80,
    )

    assert strong > weak
    assert 0 <= weak <= 100


def test_buy_side_execution_cost_consumes_ask_levels():
    result = simulate_visible_book_cost(_snapshot(), side="buy", order_size=250)

    assert result["estimated_fillable_quantity"] == 250
    assert result["estimated_weighted_avg_price_raw"] == 100_260
    assert result["mid_price_raw"] == 100_100
    assert result["spread_cost_bps"] > 0
    assert result["risk_label"] in {"low", "medium", "high"}


def test_sell_side_execution_cost_consumes_bid_levels():
    result = simulate_visible_book_cost(_snapshot(), side="sell", order_size=250)

    assert result["estimated_fillable_quantity"] == 250
    assert result["estimated_weighted_avg_price_raw"] == 99_940
    assert result["mid_price_raw"] == 100_100
    assert result["spread_cost_bps"] > 0


def test_execution_cost_warns_when_visible_depth_is_insufficient():
    result = simulate_visible_book_cost(_snapshot(), side="buy", order_size=2_000)

    assert result["visible_depth"] == 1_500
    assert result["estimated_fillable_quantity"] == 1_500
    assert result["estimated_unfilled_quantity"] == 500
    assert result["insufficient_visible_liquidity"] is True
    assert result["risk_label"] == "high"


def test_demo_mode_loads_public_safe_aggregate_data():
    demo = load_liquidityiq_demo()

    assert demo["metadata"]["mode"] == "demo"
    assert demo["liquidity_buckets"]
    assert demo["execution_snapshots"]
    assert "no raw ITCH" in demo["evidence"]["lineage"]
    serialized = str(demo).lower()
    assert "part-000" not in serialized
    assert ".parquet" not in serialized
    assert "sequence_number" not in serialized
