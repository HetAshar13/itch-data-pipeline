# Streamlit App

This app is a thin presentation layer over existing pipeline artifacts. It reads:

- `manifest.json`
- `validation_report.json`
- `message_events` Parquet
- DuckDB-derived message type counts
- optional `order_events` Parquet and DuckDB summaries when those artifacts exist

It does not parse raw ITCH files and does not implement pipeline logic.

Run from the repo root after generating local artifacts:

```powershell
streamlit run app/streamlit_app.py
```
