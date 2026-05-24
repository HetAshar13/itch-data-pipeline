# Week 2 Plan

## Goal

Build the first small local processing path around a MeatPy sample file.

## Target

One small run should produce:

- a manifest JSON
- one small MeatPy-derived JSON summary
- a clear folder structure

## Current sample path

Use the manifest-backed peek command:

```powershell
python -m itch_data_pipeline.cli sample-peek-run --input data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz --limit 10 --output-root outputs\local
```

This writes:

- `outputs/local/dataset=message_peek/date=unknown/symbol=ALL/summary.json`
- `outputs/local/dataset=message_peek/date=unknown/symbol=ALL/manifest.json`

`summary.json` records what MeatPy saw in the first N messages.

`manifest.json` records how the run happened: input path, input SHA-256, output path, message count, MeatPy probe result, status, timestamps, and validation status.

## Tasks

1. Get a MeatPy sample file working locally or identify why it must run on HPC.
2. Add a tiny `peek-itch50` command to inspect the first N messages.
3. Add `sample-peek-run` to write a summary JSON and manifest JSON.
4. Review the generated outputs and decide what metadata is useful.
5. Only then decide whether `process_symbol_day` is ready for a tiny skeleton.
6. Document what worked and what did not.

## Do not do yet

- no full `process_symbol_day` implementation
- no custom ITCH parser
- no Parquet dataset writing
- no full validation engine
- no SLURM array
- no Streamlit
- no dbt
- no Spark
- no Prefect
