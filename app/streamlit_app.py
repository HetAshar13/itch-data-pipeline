from __future__ import annotations

import pandas as pd
import streamlit as st

from itch_data_pipeline.reporting.showcase_context import load_showcase_context


st.set_page_config(
    page_title="ITCH Pipeline Showcase",
    layout="wide",
)

st.title("HPC Market Data Engineering Pipeline")
st.caption("Week 4 showcase: real Nasdaq BX ITCH sample -> MeatPy -> Parquet -> validation -> DuckDB summary")

with st.sidebar:
    st.header("Run Selection")
    output_root = st.text_input("Output root", value="outputs/local")
    date = st.text_input("Date partition", value="2019-12-30")
    symbol = st.text_input("Symbol partition", value="ALL")
    top_n = st.number_input("Top message types", min_value=1, max_value=50, value=10, step=1)
    sample_rows = st.number_input("Sample rows", min_value=1, max_value=100, value=20, step=1)

try:
    context = load_showcase_context(
        output_root=output_root,
        date=date,
        symbol=symbol,
        top_n=int(top_n),
        sample_rows=int(sample_rows),
    )
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

manifest = context["manifest"]
validation = context["validation"]
row_count = manifest["row_counts"]["message_events"]

metric_cols = st.columns(4)
metric_cols[0].metric("Rows extracted", f"{row_count:,}")
metric_cols[1].metric("Run status", manifest["status"])
metric_cols[2].metric("Validation status", validation["status"])
metric_cols[3].metric("Rules failed", validation["rules_failed"])

st.subheader("Run Metadata")
metadata_cols = st.columns(2)
with metadata_cols[0]:
    st.write("Input file")
    st.code(manifest["input_file"], language="text")
    st.write("Input SHA-256")
    st.code(manifest["input_sha256"], language="text")
with metadata_cols[1]:
    st.write("Parquet dataset")
    st.code(context["parquet_path"], language="text")
    st.write("Validation report")
    st.code(context["validation_report_path"], language="text")

st.subheader("Top Message Types")
top_message_types = pd.DataFrame(context["top_message_types"])
st.dataframe(top_message_types, width="stretch", hide_index=True)
if not top_message_types.empty:
    chart_data = top_message_types.set_index("message_type")["row_count"]
    st.bar_chart(chart_data)

st.subheader("Structural Validation Findings")
findings = pd.DataFrame(validation["findings"])
st.dataframe(findings, width="stretch", hide_index=True)

st.subheader("Sample Message Events")
st.dataframe(pd.DataFrame(context["sample_rows"]), width="stretch", hide_index=True)

order_events = context["order_events"]
if order_events["available"]:
    st.subheader("Week 6 Order Events")
    order_manifest = order_events["manifest"]
    order_validation = order_events["validation"]
    order_row_count = order_manifest["row_counts"]["order_events"]

    order_metric_cols = st.columns(3)
    order_metric_cols[0].metric("Order events", f"{order_row_count:,}")
    order_metric_cols[1].metric("Order validation", order_validation["status"])
    order_metric_cols[2].metric("Order rules failed", order_validation["rules_failed"])

    st.write("Order events Parquet")
    st.code(order_events["parquet_path"], language="text")

    order_summary = order_events["summary"]
    st.write("Order Event Counts")
    st.dataframe(pd.DataFrame(order_summary["event_counts"]), width="stretch", hide_index=True)
    st.write("Add Order Side Counts")
    st.dataframe(pd.DataFrame(order_summary["side_counts"]), width="stretch", hide_index=True)
    st.write("Top Stocks By Add Events")
    st.dataframe(pd.DataFrame(order_summary["top_stocks_by_adds"]), width="stretch", hide_index=True)
    st.write("Sample Order Events")
    st.dataframe(pd.DataFrame(order_events["sample_rows"]), width="stretch", hide_index=True)

st.subheader("What This Demo Shows")
st.markdown(
    """
- MeatPy reads a real Nasdaq BX ITCH sample file.
- The pipeline writes a bounded, partitioned Parquet dataset.
- The manifest records reproducibility metadata.
- Structural validation checks the output before presentation.
- DuckDB-style analytics summarize the Parquet output.
- When Week 6 artifacts exist, order-event summaries are presented without running extraction.
"""
)

st.subheader("Current Boundaries")
st.markdown(
    """
- This app does not parse raw ITCH files.
- It does not reconstruct the full order book.
- It does not run SLURM jobs yet.
- It is a presentation layer over existing pipeline artifacts.
"""
)
