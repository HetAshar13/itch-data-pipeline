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


def _inject_theme() -> None:
    st.markdown(
        """
<style>
:root {
  --liq-bg: #070a0f;
  --liq-panel: #10151f;
  --liq-panel-2: #151c29;
  --liq-line: #253042;
  --liq-text: #edf3ff;
  --liq-muted: #9aa8bd;
  --liq-cyan: #39d0ff;
  --liq-green: #6ef2a0;
  --liq-amber: #f2c96b;
  --liq-red: #ff6b7a;
}

.stApp {
  background: var(--liq-bg);
  color: var(--liq-text);
}

[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu {
  visibility: hidden;
}

[data-testid="stSidebar"] {
  background: #0b1018;
  border-right: 1px solid var(--liq-line);
}

[data-testid="stSidebar"] * {
  color: var(--liq-text);
}

.block-container {
  padding-top: 2rem;
  padding-bottom: 3rem;
  max-width: 1500px;
}

h1, h2, h3 {
  letter-spacing: 0;
}

.hero {
  border: 1px solid var(--liq-line);
  background: linear-gradient(135deg, #0b111b 0%, #101726 55%, #0b1118 100%);
  border-radius: 8px;
  padding: 28px 30px;
  margin-bottom: 20px;
}

.eyebrow {
  color: var(--liq-cyan);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08rem;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.hero-title {
  color: var(--liq-text);
  font-size: clamp(2.1rem, 5vw, 4.3rem);
  line-height: 0.98;
  font-weight: 800;
  margin: 0;
}

.hero-subtitle {
  color: var(--liq-muted);
  font-size: 1.05rem;
  line-height: 1.6;
  max-width: 880px;
  margin-top: 16px;
  margin-bottom: 0;
}

.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.pill {
  border: 1px solid var(--liq-line);
  background: #0c131d;
  color: var(--liq-muted);
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 650;
}

.metric-card {
  border: 1px solid var(--liq-line);
  background: var(--liq-panel);
  border-radius: 8px;
  padding: 17px 18px;
  min-height: 112px;
}

.metric-label {
  color: var(--liq-muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06rem;
}

.metric-value {
  color: var(--liq-text);
  font-size: clamp(1.28rem, 2.2vw, 1.72rem);
  line-height: 1.15;
  font-weight: 800;
  margin-top: 10px;
  word-break: keep-all;
}

.metric-note {
  color: var(--liq-muted);
  font-size: 0.82rem;
  margin-top: 8px;
}

.panel {
  border: 1px solid var(--liq-line);
  background: var(--liq-panel);
  border-radius: 8px;
  padding: 18px;
  margin-top: 12px;
}

.section-title {
  color: var(--liq-text);
  font-size: 1.22rem;
  font-weight: 800;
  margin: 0 0 4px 0;
}

.section-copy {
  color: var(--liq-muted);
  font-size: 0.92rem;
  margin: 0 0 12px 0;
}

.status-stable {
  color: var(--liq-green);
}

.status-watch {
  color: var(--liq-amber);
}

.status-stressed, .status-high {
  color: var(--liq-red);
}

.status-medium {
  color: var(--liq-amber);
}

.status-low {
  color: var(--liq-green);
}

div[data-testid="stMetric"] {
  background: var(--liq-panel);
  border: 1px solid var(--liq-line);
  border-radius: 8px;
  padding: 14px 16px;
}

div[data-testid="stMetric"] label {
  color: var(--liq-muted) !important;
}

div[data-testid="stMetricValue"] {
  color: var(--liq-text);
}

.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}

.stTabs [data-baseweb="tab"] {
  background: #0c131d;
  border: 1px solid var(--liq-line);
  border-radius: 8px;
  padding: 10px 14px;
}

.stTabs [aria-selected="true"] {
  background: #132031;
  border-color: var(--liq-cyan);
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--liq-line);
  border-radius: 8px;
  overflow: hidden;
}

button, input, textarea, [data-baseweb="select"] {
  border-radius: 8px !important;
}

div[data-testid="stHeadingWithActionElements"] h1 {
  position: absolute;
  left: -10000px;
  height: 1px;
  overflow: hidden;
}
</style>
""",
        unsafe_allow_html=True,
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


def _metric_card(label: str, value: str, note: str = "", status: str | None = None) -> None:
    status_class = f" status-{status}" if status else ""
    st.markdown(
        f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value{status_class}">{value}</div>
  <div class="metric-note">{note}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _section(title: str, copy: str) -> None:
    st.markdown(
        f"""
<div class="panel">
  <div class="section-title">{title}</div>
  <p class="section-copy">{copy}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def _format_optional(value: object, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:,.2f}{suffix}"
    return f"{value}{suffix}"


_inject_theme()

st.markdown(
    """
<div class="hero">
  <div class="eyebrow">Execution liquidity intelligence</div>
  <div class="hero-title">LiquidityIQ</div>
  <p class="hero-subtitle">
    A high-signal analytics console for validated ITCH limit-order-book artifacts:
    spread, depth, imbalance, visible-book cost, market quality, and audit-ready lineage.
  </p>
  <div class="pill-row">
    <span class="pill">Read-only app</span>
    <span class="pill">Public-safe demo mode</span>
    <span class="pill">No raw ITCH in Git</span>
    <span class="pill">Visible top-5 book model</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)
st.title("LiquidityIQ")

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
    stress_count = int((bars["stress_regime"] != "stable").sum())

    metric_cols = st.columns(4)
    with metric_cols[0]:
        _metric_card("Liquidity score", f"{avg_score:.1f}", "Average score across visible buckets", "stable")
    with metric_cols[1]:
        _metric_card("Symbols", f"{symbols_count}", "ETF universe loaded into this view")
    with metric_cols[2]:
        _metric_card("Stress windows", f"{stress_count}", "Buckets labelled watch or stressed", "watch")
    with metric_cols[3]:
        _metric_card("Validation", str(validation_status), "Artifact-level evidence status", "stable")

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

    _section(
        "Symbol quality comparison",
        "Higher scores reflect tighter spreads, deeper visible top-5 book depth, stronger two-sided coverage, and lower imbalance pressure.",
    )
    st.dataframe(comparison, width="stretch", hide_index=True)

with tabs[1]:
    st.subheader("Liquidity Timeline")
    selected_symbol = st.selectbox("Timeline symbol", sorted(bars["symbol"].unique()))
    symbol_bars = bars[bars["symbol"] == selected_symbol].sort_values("bucket_start_ns")
    chart_frame = symbol_bars.set_index("bucket_minute")

    metric_cols = st.columns(3)
    with metric_cols[0]:
        _metric_card(
            "Average spread",
            _format_optional(float(symbol_bars["avg_spread_1_raw"].mean()), " raw"),
            "Lower is better for execution cost",
        )
    with metric_cols[1]:
        _metric_card(
            "Average top-5 depth",
            f"{float(symbol_bars['avg_total_depth_top5'].mean()):,.0f}",
            "Displayed bid plus ask depth",
            "stable",
        )
    with metric_cols[2]:
        _metric_card(
            "Two-sided coverage",
            f"{float(symbol_bars['two_sided_snapshot_percent'].mean()):.2f}%",
            "Percent of snapshots with both bid and ask",
            "stable",
        )

    line_cols = st.columns(3)
    with line_cols[0]:
        _section("Spread", "Raw level-1 spread by minute bucket.")
        st.line_chart(chart_frame[["avg_spread_1_raw"]])
    with line_cols[1]:
        _section("Top-5 depth", "Average displayed depth across bid and ask levels.")
        st.line_chart(chart_frame[["avg_total_depth_top5"]])
    with line_cols[2]:
        _section("Imbalance", "Level-1 pressure between displayed bid and ask size.")
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
        with result_cols[0]:
            _metric_card("Fillable", f"{scenario['estimated_fillable_quantity']:,}", "Shares visible in top 5")
        with result_cols[1]:
            _metric_card("Visible depth", f"{scenario['visible_depth']:,}", "Total depth on selected side")
        with result_cols[2]:
            _metric_card("WAP", f"{scenario['estimated_weighted_avg_price_display']:.2f}", "Weighted average price")
        with result_cols[3]:
            _metric_card("Cost", f"{scenario['spread_cost_bps']:.2f} bps", "Slippage versus midpoint")
        with result_cols[4]:
            _metric_card("Risk", scenario["risk_label"], "Visible-book scenario label", str(scenario["risk_label"]))

        _section(
            "Visible-book simulator",
            "This deterministic model consumes displayed top-5 depth only. It is not market impact, trading advice, alpha, or full TCA.",
        )
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

    event_total = int(market_quality["event_count"].sum())
    avg_cancel = _safe_mean(market_quality, "cancel_to_add_ratio")
    avg_execute = _safe_mean(market_quality, "execute_to_add_ratio")
    quality_cols = st.columns(3)
    with quality_cols[0]:
        _metric_card("Event intensity", f"{event_total:,}", "Matched order-event rows")
    with quality_cols[1]:
        _metric_card("Cancel/add", f"{avg_cancel:.2f}", "Higher can indicate churn", "watch")
    with quality_cols[2]:
        _metric_card("Execute/add", f"{avg_execute:.2f}", "Execution rate proxy")

    st.dataframe(market_quality, width="stretch", hide_index=True)

    ratio_frame = market_quality.groupby("symbol", as_index=False).agg(
        cancel_to_add_ratio=("cancel_to_add_ratio", "mean"),
        execute_to_add_ratio=("execute_to_add_ratio", "mean"),
        event_count=("event_count", "sum"),
    )
    st.bar_chart(ratio_frame.set_index("symbol")[["cancel_to_add_ratio", "execute_to_add_ratio"]])

with tabs[4]:
    st.subheader("Evidence")
    evidence_cols = st.columns(3)
    with evidence_cols[0]:
        _metric_card("Mode", str(metadata.get("mode", "unknown")), "Demo uses aggregate public-safe data")
    with evidence_cols[1]:
        _metric_card("Price scale", f"{metadata.get('price_scale', PRICE_SCALE):,}", "Display price conversion")
    with evidence_cols[2]:
        _metric_card("Boundary", "read-only", "No extraction or mutation", "stable")

    evidence_panels = st.columns(2)
    with evidence_panels[0]:
        _section("Metadata", "Run context and demo/local artifact selection.")
        st.json(metadata)
    with evidence_panels[1]:
        _section("Lineage and limits", "Validation, raw-data policy, and visible-book modeling boundary.")
        st.json(evidence)

    st.markdown(
        """
LiquidityIQ is read-only over existing artifacts. It does not parse raw ITCH,
run MeatPy extraction, submit SLURM jobs, or mutate pipeline outputs. Demo mode
uses aggregate public-safe data only; local artifact mode reads private generated
Parquet and JSON artifacts when present.
"""
    )
