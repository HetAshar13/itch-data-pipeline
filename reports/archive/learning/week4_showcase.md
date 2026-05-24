# Week 4 Showcase Report

## Summary

This report demonstrates a bounded, reproducible data engineering path over a real Nasdaq BX ITCH sample file.

## Input And Run Metadata

- Input file: `data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz`
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Date partition: `2019-12-30`
- Symbol partition: `ALL`
- Max messages: `100000`
- Rows written: `100000`
- Run status: `success`
- Validation status: `passed`

## Output Artifacts

- Parquet dataset: `outputs\local\dataset=message_events\date=2019-12-30\symbol=ALL\part-000.parquet`
- Manifest: `outputs\local\dataset=message_events\date=2019-12-30\symbol=ALL\manifest.json`
- Validation report: `outputs\local\dataset=message_events\date=2019-12-30\symbol=ALL\validation_report.json`

## Top Message Types

| Message Type | MeatPy Class | Row Count |
| --- | --- | ---: |
| A | AddOrderMessage | 29235 |
| D | OrderDeleteMessage | 28943 |
| R | StockDirectoryMessage | 8906 |
| H | StockTradingActionMessage | 8900 |
| Y | RegSHOMessage | 8897 |
| N | RpiiMessage | 7813 |
| L | MarketParticipantPositionMessage | 6171 |
| U | OrderReplaceMessage | 771 |
| X | OrderCancelMessage | 299 |
| E | OrderExecutedMessage | 47 |

## What This Proves

- MeatPy can read the real ITCH sample.
- The project can write partitioned Parquet output.
- The manifest records reproducibility metadata.
- Structural validation checks the output shape and row count consistency.
- DuckDB can query the Parquet output directly.
- The Streamlit app exists as a thin presentation layer over these artifacts.

## What This Does Not Prove Yet

- It does not prove full order book correctness.
- It does not implement full symbol/day processing.
- It does not run SLURM jobs yet.
- It does not make Streamlit responsible for pipeline execution.
