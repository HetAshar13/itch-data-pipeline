# Week 7-9 LOB Status

Use this file to resume the LOB phase after context compaction or a new chat.

## Current Position

- Week 7: complete.
- Week 8: complete enough locally.
- Week 9: validation and DuckDB analytics complete locally.
- Week 10 HPC LOB run: complete for `SPY`.

The next checkpoint should either document the Week 10 result or begin Week 11
multi-symbol planning.

## Learning Rule

Learning is still the main focus.

For every next slice:

1. Explain the concept.
2. Ask one reasoning question.
3. Stop and wait for the student's answer.
4. Respond to the answer and correct gaps.
5. Implement only the tiny slice.
6. Run focused tests and then the full suite.
7. Give one interview-style question and answer direction.

## Completed LOB Work

Week 7 proved MeatPy LOB mechanics with synthetic messages:

- add creates a bid/ask level,
- non-target symbols are ignored,
- cancel reduces volume,
- replace updates order ref, price, and volume,
- delete removes the order.

Week 8 added the local `lob_snapshots` path:

- `lob_to_snapshot_row()` maps one MeatPy book state into a fixed top-5 row.
- `extract_lob_snapshot_rows()` streams bounded messages and returns rows in memory.
- `run_extract_lob_snapshots_sample()` writes Parquet plus manifest.
- CLI command: `extract-lob-snapshots-sample`.

Week 9 validation so far:

- Validation module: `src/itch_data_pipeline/validation/lob_snapshots.py`
- CLI command: `validate-lob-snapshots`
- Current rules:
  - Parquet file exists,
  - expected columns present,
  - positive row count,
  - manifest row count matches Parquet,
  - single requested symbol,
  - sequence numbers increasing,
  - timestamps non-decreasing,
  - top of book not crossed where both sides exist.

Week 9 analytics so far:

- Analytics module: `src/itch_data_pipeline/analytics/lob_snapshots.py`
- CLI command: `query-lob-summary`
- The command reads existing `lob_snapshots` Parquet with DuckDB and does not rerun extraction.
- It returns snapshot count, first/last timestamp, two-sided snapshot count/percent, raw spread summary, and average level-1 imbalance.

Week 10 preparation so far:

- Reusable SLURM script: `hpc/submit_lob_snapshots.slurm`
- The script is parameterized with environment variables:
  - `ITCH_INPUT`
  - `ITCH_DATE`
  - `SYMBOL`
  - `OUTPUT_ROOT`
  - `MAX_MESSAGES`
  - `SUMMARY_PATH`
- It runs health checks, extraction, validation, and DuckDB summary.
- It was submitted on Iris as SLURM job `5404108` and completed successfully.

Week 10 HPC result:

- Compute node: `iris-111`
- Symbol: `SPY`
- Max messages: `2000000`
- Rows written: `59163`
- Validation: `8` rules run, `0` failed, status `passed`
- Two-sided snapshots: `59104`
- Two-sided percent: `99.9002755100316`
- Median raw spread: `300.0`
- Average raw spread: `351.1166756903086`
- Local proof directory: `logs/week10_lob_5404108/`

## Current Local LOB Artifact

Command used:

```powershell
.\.venv\Scripts\python.exe -m itch_data_pipeline.cli extract-lob-snapshots-sample --input data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz --date 2019-12-30 --symbol SPY --max-messages 100000 --output-root outputs\local
```

Result:

- `max_messages`: `100000`
- `rows_written`: `5358`
- Parquet: `outputs/local/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/part-000.parquet`
- Manifest: `outputs/local/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/manifest.json`

Validation command:

```powershell
.\.venv\Scripts\python.exe -m itch_data_pipeline.cli validate-lob-snapshots --output-root outputs\local --date 2019-12-30 --symbol SPY
```

Validation result:

- status: `passed`
- rules run: `8`
- rules failed: `0`
- report: `outputs/local/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/validation_report.json`

DuckDB summary command:

```powershell
.\.venv\Scripts\python.exe -m itch_data_pipeline.cli query-lob-summary --output-root outputs\local --date 2019-12-30 --symbol SPY
```

DuckDB summary result:

- snapshot count: `5358`
- first timestamp ns: `25204435833095`
- last timestamp ns: `31020465281748`
- two-sided snapshot count: `5309`
- two-sided snapshot percent: `99.08547965658828`
- average raw spread: `808.6645319269165`
- median raw spread: `700.0`
- min raw spread: `100`
- max raw spread: `6000`
- average level-1 imbalance: `-0.23431683727807356`

## Current Test Status

Latest full local suite:

- `81 passed`

## Concepts The Student Has Learned

- LOB means limit order book: resting bid/ask orders for one symbol.
- ITCH is an event stream, not a ready-made book table.
- MeatPy parses ITCH and reconstructs the book; this project builds the engineering layer.
- `order_events` preserves individual event history.
- `lob_snapshots` stores derived book state at moments in the event stream.
- Top-5 depth gives a stable schema and captures the most important book levels.
- Raw ITCH prices are stored first to avoid premature normalization claims.
- `max_messages` is the input scan bound; `rows_written` is the number of emitted snapshots.
- One-sided book rows are allowed; crossed-book checks only apply when both bid and ask exist.
- Sequence numbers should increase; timestamps may be equal but should not go backward.
- `query-lob-summary` is read-only analytics over existing validated Parquet.
- `two_sided_snapshot_percent` measures how often both best bid and best ask exist.
- Spread and mid-price are meaningful only when both sides exist.

## Next Smallest Checkpoint

Decide how to present or extend the completed Week 10 result.

Before implementing, ask the student:

Why is the Week 10 `SPY` run stronger proof than the earlier local `SPY` smoke run?

Stop and wait for the student's answer.

## Week 10 Direction

Week 10 used Iris HPC after local LOB analytics were complete.

Completed first HPC LOB run:

- symbol: `SPY`
- date: `2019-12-30`
- max messages: `2000000`
- output root: private Iris scratch path
- run through SLURM, not the access node

Copy back only small proof artifacts:

- SLURM logs,
- manifest,
- validation report,
- DuckDB summary/report.

Do not copy raw data or large Parquet files into Git.
