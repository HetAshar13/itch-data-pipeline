# Portfolio Case Study: HPC Market Data Engineering Pipeline

## Executive Summary

This project is a production-oriented data engineering pipeline for processing
Nasdaq ITCH market data into validated, partitioned analytical artifacts. It
uses MeatPy for ITCH parsing and limit order book reconstruction, DuckDB for
local analytics over Parquet, Streamlit for the read-only LiquidityIQ product
layer, and Iris HPC with SLURM for larger proof runs.

The project demonstrates the engineering work around a difficult data source:
lineage, validation, reproducibility, operational runbooks, safe handling of
licensed raw data, shareable evidence artifacts, and business-facing liquidity
analytics.

## Problem

Nasdaq ITCH data is a high-volume binary event stream, not a ready-made table.
To analyze it reliably, the pipeline must:

- parse messages without writing a custom ITCH parser,
- preserve enough audit detail to explain what was processed,
- reconstruct symbol-specific limit order book state through MeatPy,
- store outputs in stable partitioned datasets,
- validate outputs before analytics,
- run larger workloads on HPC without copying raw data into Git,
- produce public-safe evidence for review.

## Architecture

```text
Private raw ITCH file on disk or Iris scratch
        |
        v
MeatPy parser and LOB reconstruction
        |
        v
Pipeline runners
  - message_events
  - order_events
  - lob_snapshots
        |
        v
Partitioned Parquet + manifest + validation JSON
        |
        v
DuckDB summaries + reports + Streamlit presentation
        |
        v
LiquidityIQ analytics product
  - spread, depth, imbalance
  - visible-book execution cost estimates
  - market-quality regimes
        |
        v
Copied proof artifacts for professor/recruiter review
```

Raw Nasdaq data and large generated Parquet outputs remain outside Git. The
shareable repository contains code, tests, docs, reports, SLURM logs, manifests,
validation JSON files, DuckDB summaries, and small proof bundles.

## Data Products

### `message_events`

Broad audit dataset generated from parsed MeatPy messages.

- Partition path: `outputs/<root>/dataset=message_events/date=<date>/symbol=ALL/part-000.parquet`
- Purpose: preserve a broad event-level view for audit and message-type analysis.
- Iris proof: `1,000,000` rows from SLURM job `5386100`.
- Validation: `4` rules run, `0` failed.

### `order_events`

Focused order-event dataset derived from MeatPy message objects.

- Partition path: `outputs/<root>/dataset=order_events/date=<date>/symbol=ALL/part-000.parquet`
- Purpose: expose add, cancel, delete, replace, and execution events for analysis.
- Iris proof: `796,151` rows from SLURM job `5386100`.
- Validation: `7` rules run, `0` failed.

### `lob_snapshots`

Symbol-specific top-5 limit order book snapshot dataset.

- Partition path: `outputs/<root>/dataset=lob_snapshots/date=<date>/symbol=<symbol>/part-000.parquet`
- Purpose: capture derived book state after MeatPy applies LOB-changing events.
- Scope: top 5 bid and ask levels, raw ITCH price units.
- Validation: `8` structural and sanity rules per validated run.

### `liquidity_bars`

Derived analytics mart used by LiquidityIQ.

- Grain: symbol, date, and 1-minute time bucket.
- Purpose: convert validated LOB and order-event artifacts into business-facing
  liquidity diagnostics.
- Metrics: raw/display spread, top-5 bid/ask depth, level-1 imbalance,
  two-sided book coverage, event intensity, cancel/add ratio, execute/add ratio,
  liquidity score, and stress regime.
- Boundary: keeps source prices in raw ITCH units and adds separate display
  prices using an explicit `10,000` scale.

## Validation Strategy

Validation is intentionally layered:

- Structural checks: artifact exists, expected columns exist, row count is positive.
- Lineage checks: manifest row counts match Parquet output and input SHA-256 is recorded.
- Partition checks: requested date and symbol are consistent.
- Ordering checks: sequence numbers increase and timestamps do not go backwards.
- Market sanity checks: top of book is not crossed when both bid and ask exist.

This validation proves that the generated artifacts are structurally consistent
and analytically usable. It does not prove complete market microstructure correctness
or exchange-level matching behavior.

## Analytics Layer

DuckDB is used to query generated Parquet files directly. This keeps analytics
lightweight and reproducible: no database server, no warehouse dependency, and
no file upload step.

The pipeline produces summaries such as:

- message type counts,
- order event counts,
- top symbols by add-event count and shares,
- LOB snapshot counts,
- first and last timestamps,
- two-sided snapshot percentage,
- average and median raw spread,
- level-1 imbalance summary.

LiquidityIQ extends this into a business-facing analytics layer:

- executive liquidity scorecards,
- spread, depth, and imbalance timelines,
- deterministic visible-book execution cost scenarios,
- market-quality ratios and stress labels,
- evidence metadata for lineage and validation status.

Streamlit reads existing artifacts only. It does not trigger extraction,
validation, raw ITCH access, SLURM submission, or data mutation.

## HPC Proof

The project uses Iris HPC through SLURM for larger runs. SLURM job IDs, compute
node names, logs, manifests, validation reports, and summary JSON files are kept
as proof artifacts.

### Bounded Message And Order Event Run

| Dataset | Job ID | Node | Rows | Validation |
| --- | --- | --- | ---: | --- |
| `message_events` | `5386100` | `iris-111` | `1,000,000` | passed |
| `order_events` | `5386100` | `iris-111` | `796,151` | passed |

### 10M Multi-Symbol LOB Run

| Symbol | Job ID | Max Messages | Snapshots | Two-Sided % | Median Spread Raw | Validation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| SPY | `5404209` | `10,000,000` | `206,927` | `99.9715%` | `300.0` | passed |
| QQQ | `5404299` | `10,000,000` | `172,052` | `99.5054%` | `300.0` | passed |
| IWM | `5404485` | `10,000,000` | `156,647` | `99.5059%` | `300.0` | passed |

Total copied-proof snapshots across the 10M comparison: `535,626`.

### SPY Until-EOF LOB Run

| Symbol | Job ID | Node | Stop Reason | Messages Scanned | Snapshots | Two-Sided % | Median Spread Raw | Validation |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| SPY | `5406828` | `iris-111` | `eof` | `29,156,757` | `614,578` | `99.9513%` | `200.0` | passed |

This is the strongest single-symbol proof in the project: the SPY LOB pipeline
ran until the ITCH reader reached EOF and recorded explicit stop metadata.

## Reproducibility

The public-safe workflow has three levels:

- Local Windows: create `.venv`, install requirements, run CLI smoke commands and tests.
- Docker: build a clean Python 3.11 runtime and run tests without raw Nasdaq data.
- Iris HPC: submit SLURM jobs against private scratch data and copy back only proof artifacts.

Current verification:

- Local suite: `137 passed`.
- Docker image: `docker build -t itch-data-pipeline:test .` succeeds.
- Docker test runtime supports pytest, healthcheck, and raw-data safety checks
  without bundled raw Nasdaq data.

## Data Governance

Nasdaq ITCH data is licensed and must not be committed or shared. The project
enforces this through process and tooling:

- raw data stays in ignored local or Iris scratch paths,
- generated large Parquet files stay outside public artifacts,
- proof bundles include logs, manifests, validation JSON, and summaries only,
- CI includes a raw-data safety check,
- Docker excludes raw data and generated outputs.

## What This Demonstrates For Data Engineering Roles

- Designing a small but complete data pipeline around a difficult binary source.
- Using a trusted domain library instead of writing a custom parser.
- Building partitioned data products with explicit contracts.
- Separating extraction, validation, analytics, reporting, and presentation.
- Running larger jobs through HPC scheduling and preserving operational evidence.
- Creating reproducible public-safe artifacts without exposing licensed data.
- Writing tests for CLI behavior, validation, analytics, Docker configuration, reports, and safety checks.
- Turning validated engineering artifacts into a practical analytics product for
  execution liquidity and market-quality review.

## Limitations

- Core LOB prices remain raw ITCH integer units; LiquidityIQ display prices are
  separate derived fields using an explicit scale.
- Validation is structural plus sanity checking, not a formal proof of exchange correctness.
- Multi-symbol comparisons are bounded by message count; only SPY has an until-EOF LOB run.
- Large Parquet outputs remain private and are not part of the public portfolio repo.
- Visible-book cost estimates use displayed top-5 depth only. They are not full
  transaction cost analysis, market-impact modeling, trading advice, or alpha.
- Streamlit is read-only over existing artifacts and aggregate demo data.

## Lessons Learned

- Start with narrow, testable datasets before scaling to HPC.
- Preserve both broad audit data and focused analytical data.
- Validate artifacts before querying them.
- Use manifests and input hashes to make results traceable.
- Treat HPC logs, job IDs, and copied proof files as first-class evidence.
- Keep public portfolio artifacts useful without leaking raw or proprietary data.
