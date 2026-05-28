from __future__ import annotations

import pandas as pd
import streamlit as st

from itch_data_pipeline.analytics.liquidityiq import (
    PRICE_SCALE,
    liquidityiq_from_artifacts,
    load_liquidityiq_demo,
    simulate_visible_book_cost,
)


st.set_page_config(
    page_title="LiquidityIQ",
    layout="wide",
)


def _load_context(mode: str, output_root: str, date: str, symbols: list[str]) -> dict:
    if mode == "demo":
        return load_liquidityiq_demo()

    context = liquidityiq_from_artifacts(
        output_root=output_root,
        date=date,
        symbols=symbols,
    )
    if context["liquidity_buckets"]:
        return context

    st.warning("No local LOB artifacts were found for the selected partition. Showing public-safe demo aggregates.")
    return load_liquidityiq_demo()


def _as_frame(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _format_bucket_labels(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "bucket_start_ns" not in frame:
        return frame
    frame = frame.copy()
    frame["bucket_minute"] = (frame["bucket_start_ns"] // 60_000_000_000).astype(str)
    return frame


def _safe_mean(frame: pd.DataFrame, column: str) -> float:
    if frame.empty or column not in frame:
        return 0.0
    return float(frame[column].mean())


st.title("LiquidityIQ")
st.caption(
    "Execution liquidity intelligence from validated ITCH limit-order-book artifacts: "
    "spread, depth, imbalance, visible-book cost, market quality, and lineage."
)

with st.sidebar:
    st.header("Data Mode")
    mode = st.selectbox("Mode", options=["demo", "local_artifacts"], index=0)
    output_root = st.text_input("Output root", value="outputs/local")
    date = st.text_input("Date", value="2019-12-30")
    symbols_text = st.text_input("Symbols", value="SPY,QQQ,IWM")
    symbols = [symbol.strip().upper() for symbol in symbols_text.split(",") if symbol.strip()]

context = _load_context(mode, output_root, date, symbols)
metadata = context.get("metadata", {})
evidence = context.get("evidence", {})
bars = _format_bucket_labels(_as_frame(context.get("liquidity_buckets", [])))
snapshots = _as_frame(context.get("execution_snapshots", []))

if bars.empty:
    st.error("LiquidityIQ has no aggregate bars to display.")
    st.stop()

tabs = st.tabs(
    [
        "Executive Overview",
        "Liquidity Timeline",
        "Execution Cost Lab",
        "Market Quality",
        "Evidence",
    ]
)

with tabs[0]:
    st.subheader("Executive Overview")
    symbols_count = bars["symbol"].nunique()
    avg_score = _safe_mean(bars, "liquidity_score")
    worst_bucket = bars.sort_values("liquidity_score").iloc[0]
    validation_status = evidence.get("validation_status", "artifact-backed")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Liquidity score", f"{avg_score:.1f}")
    metric_cols[1].metric("Symbols", f"{symbols_count}")
    metric_cols[2].metric("Worst window", f"{worst_bucket['symbol']} / {worst_bucket['stress_regime']}")
    metric_cols[3].metric("Validation", validation_status)

    comparison = (
        bars.groupby("symbol", as_index=False)
        .agg(
            liquidity_score=("liquidity_score", "mean"),
            avg_spread_raw=("avg_spread_1_raw", "mean"),
            avg_total_depth_top5=("avg_total_depth_top5", "mean"),
            two_sided_percent=("two_sided_snapshot_percent", "mean"),
        )
        .sort_values("liquidity_score", ascending=False)
    )
    st.dataframe(comparison, width="stretch", hide_index=True)

with tabs[1]:
    st.subheader("Liquidity Timeline")
    selected_symbol = st.selectbox("Timeline symbol", sorted(bars["symbol"].unique()))
    symbol_bars = bars[bars["symbol"] == selected_symbol].sort_values("bucket_start_ns")
    chart_frame = symbol_bars.set_index("bucket_minute")

    line_cols = st.columns(3)
    with line_cols[0]:
        st.write("Spread")
        st.line_chart(chart_frame[["avg_spread_1_raw"]])
    with line_cols[1]:
        st.write("Top-5 depth")
        st.line_chart(chart_frame[["avg_total_depth_top5"]])
    with line_cols[2]:
        st.write("Imbalance")
        st.line_chart(chart_frame[["avg_level1_imbalance"]])

    st.dataframe(
        symbol_bars[
            [
                "bucket_minute",
                "symbol",
                "snapshot_count",
                "avg_spread_1_raw",
                "avg_spread_1_display",
                "avg_total_depth_top5",
                "avg_level1_imbalance",
                "liquidity_score",
                "stress_regime",
            ]
        ],
        width="stretch",
        hide_index=True,
    )

with tabs[2]:
    st.subheader("Execution Cost Lab")
    if snapshots.empty:
        st.info("No execution snapshots are available for the selected mode.")
    else:
        cost_cols = st.columns(4)
        cost_symbol = cost_cols[0].selectbox("Symbol", sorted(snapshots["symbol"].unique()))
        cost_side = cost_cols[1].selectbox("Side", options=["buy", "sell"])
        cost_urgency = cost_cols[2].selectbox("Urgency", options=["passive", "normal", "aggressive"], index=1)
        order_size = cost_cols[3].number_input("Order size", min_value=1, max_value=1_000_000, value=50_000, step=1_000)

        snapshot_rows = snapshots[snapshots["symbol"] == cost_symbol].to_dict(orient="records")
        scenario = simulate_visible_book_cost(
            snapshot_rows[-1],
            side=cost_side,
            order_size=int(order_size),
            urgency=cost_urgency,
            price_scale=PRICE_SCALE,
        )

        result_cols = st.columns(5)
        result_cols[0].metric("Fillable quantity", f"{scenario['estimated_fillable_quantity']:,}")
        result_cols[1].metric("Visible depth", f"{scenario['visible_depth']:,}")
        result_cols[2].metric("WAP", f"{scenario['estimated_weighted_avg_price_display']:.4f}")
        result_cols[3].metric("Spread cost bps", f"{scenario['spread_cost_bps']:.2f}")
        result_cols[4].metric("Risk", scenario["risk_label"])

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "requested_shares": scenario["requested_shares"],
                        "estimated_fillable_quantity": scenario["estimated_fillable_quantity"],
                        "estimated_unfilled_quantity": scenario["estimated_unfilled_quantity"],
                        "depth_consumed_percent": scenario["depth_consumed_percent"],
                        "insufficient_visible_liquidity": scenario["insufficient_visible_liquidity"],
                        "limitation": scenario["limitation"],
                    }
                ]
            ),
            width="stretch",
            hide_index=True,
        )

with tabs[3]:
    st.subheader("Market Quality")
    market_quality = bars[
        [
            "bucket_minute",
            "symbol",
            "event_count",
            "add_count",
            "cancel_count",
            "delete_count",
            "replace_count",
            "execute_count",
            "cancel_to_add_ratio",
            "execute_to_add_ratio",
            "stress_regime",
        ]
    ].sort_values(["symbol", "bucket_minute"])
    st.dataframe(market_quality, width="stretch", hide_index=True)

    ratio_frame = market_quality.groupby("symbol", as_index=False).agg(
        cancel_to_add_ratio=("cancel_to_add_ratio", "mean"),
        execute_to_add_ratio=("execute_to_add_ratio", "mean"),
        event_count=("event_count", "sum"),
    )
    st.bar_chart(ratio_frame.set_index("symbol")[["cancel_to_add_ratio", "execute_to_add_ratio"]])

with tabs[4]:
    st.subheader("Evidence")
    evidence_cols = st.columns(2)
    with evidence_cols[0]:
        st.write("Metadata")
        st.json(metadata)
    with evidence_cols[1]:
        st.write("Evidence")
        st.json(evidence)

    st.markdown(
        """
LiquidityIQ is read-only over existing artifacts. It does not parse raw ITCH,
run MeatPy extraction, submit SLURM jobs, or mutate pipeline outputs. Demo mode
uses aggregate public-safe data only; local artifact mode reads private generated
Parquet and JSON artifacts when present.
"""
    )
