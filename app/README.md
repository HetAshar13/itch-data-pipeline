# LiquidityIQ Streamlit App

LiquidityIQ is a read-only analytics product layer over existing pipeline
artifacts. It presents liquidity bars, spread/depth/imbalance diagnostics,
visible-book execution cost estimates, market-quality ratios, and evidence
metadata.

The interface is designed as a high-contrast analytics console: compact cards,
clear status colors, styled tabs, and minimal business-facing copy.

The default `demo` mode loads tracked aggregate demo data from
`data_fixtures/liquidityiq_demo.json`, so recruiters can run the app without raw
Nasdaq data. `local_artifacts` mode reads private generated Parquet/JSON
artifacts when they exist.

The app does not parse raw ITCH, run MeatPy extraction, submit SLURM jobs, or
mutate data.

Run from the repo root:

```powershell
streamlit run app/streamlit_app.py
```
