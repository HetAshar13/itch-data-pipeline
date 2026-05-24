# Week 6 Showcase Report

## Summary

This report extends the Week 4 pipeline from generic ITCH message events to a bounded order-event dataset. It still uses MeatPy for ITCH message reading and keeps Streamlit as a presentation layer over generated artifacts.

## Run Metadata

- Input file: `data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz`
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Date partition: `2019-12-30`
- Symbol partition: `ALL`
- Message scan bound: `1000000`
- `message_events` rows: `1000000`
- `order_events` rows: `796151`
- `message_events` validation: `passed`
- `order_events` validation: `passed`

## Output Artifacts

- `message_events` Parquet: `outputs\local\dataset=message_events\date=2019-12-30\symbol=ALL\part-000.parquet`
- `message_events` manifest: `outputs\local\dataset=message_events\date=2019-12-30\symbol=ALL\manifest.json`
- `message_events` validation: `outputs\local\dataset=message_events\date=2019-12-30\symbol=ALL\validation_report.json`
- `order_events` Parquet: `outputs\local\dataset=order_events\date=2019-12-30\symbol=ALL\part-000.parquet`
- `order_events` manifest: `outputs\local\dataset=order_events\date=2019-12-30\symbol=ALL\manifest.json`
- `order_events` validation: `outputs\local\dataset=order_events\date=2019-12-30\symbol=ALL\validation_report.json`

## Top Message Types

| Message Type | MeatPy Class | Row Count |
| --- | --- | ---: |
| A | AddOrderMessage | 355097 |
| D | OrderDeleteMessage | 332461 |
| N | RpiiMessage | 167540 |
| U | OrderReplaceMessage | 67166 |
| F | AddOrderMPIDMessage | 28998 |
| Y | RegSHOMessage | 8915 |
| R | StockDirectoryMessage | 8906 |
| H | StockTradingActionMessage | 8901 |
| E | OrderExecutedMessage | 7062 |
| L | MarketParticipantPositionMessage | 6171 |

## Order Event Counts

| Event Type | Row Count |
| --- | ---: |
| add | 384095 |
| delete | 332461 |
| replace | 67166 |
| execute | 7062 |
| cancel | 5367 |

## Add Order Side Counts

| Side | Row Count | Total Shares |
| --- | ---: | ---: |
| S | 194211 | 131860740 |
| B | 189884 | 125411200 |

## Top Stocks By Add Events

| Stock | Add Count | Total Add Shares |
| --- | ---: | ---: |
| SPY | 11908 | 2842467 |
| QQQ | 10334 | 2409774 |
| TQQQ | 8140 | 1141374 |
| UGAZ | 7434 | 1374200 |
| IWM | 5380 | 2946400 |
| KOLD | 4429 | 825500 |
| UCO | 4208 | 4647300 |
| USO | 4008 | 33414600 |
| SQQQ | 3235 | 1293363 |
| VXX | 2980 | 1019207 |

## What This Proves

- MeatPy can read the real ITCH sample without a custom parser.
- The project can derive a second, order-event-focused Parquet dataset.
- Both datasets have manifests and structural validation reports.
- DuckDB can query message-level and order-event-level outputs directly.
- Streamlit can present Week 6 artifacts without running pipeline logic.

## What This Does Not Prove Yet

- It does not reconstruct the full order book.
- It does not prove market microstructure correctness.
- It does not normalize raw ITCH price integers into display prices.
- It does not add Spark, Airflow, Kafka, Snowflake, or ML.
