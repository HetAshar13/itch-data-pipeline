# Professor LOB Attachments Review

This note summarizes the files received from the professor for possible future use.

The attachment archive itself is not copied into the repo. The review below keeps only high-level technical notes.

## Summary

The attachments are useful as reference material for a future LOB phase, but they should not be imported directly into this project yet.

They show a MeatPy-based path toward:

- downloading raw Nasdaq ITCH files,
- extracting one symbol from multi-symbol ITCH data,
- using MeatPy's market processor and limit order book classes,
- producing LOB snapshot Parquet files,
- computing rolling order-flow features,
- running the workflow through SLURM.

This is relevant to the project roadmap, but it is broader than the current learning checkpoint.

## Useful Files By Role

### Symbol Extraction

`B_extract_stock_meatpy.py` shows how to use MeatPy's `ITCH50MessageReader` and `ITCH50Writer` to extract messages for a single symbol into a smaller `.itch50.gz` file.

Useful ideas:

- use MeatPy for symbol-aware extraction,
- keep raw data processing on HPC,
- parallelize across daily files with care,
- write one output per symbol/day.

This could help later if the project moves from `symbol=ALL` bounded samples to symbol-specific processing.

### LOB Reconstruction Reference

`C_LOB_meatpy.py` is the most important reference file.

It uses MeatPy concepts such as:

- `ITCH50MarketProcessor`,
- `LimitOrderBook`,
- `LOBRecorder`,
- LOB bid/ask levels,
- snapshot timestamps,
- order-flow aggregation windows.

Useful ideas:

- let MeatPy handle the order book mechanics,
- do not write a custom raw ITCH parser,
- separate event handling from snapshot recording,
- record LOB snapshots at a fixed interval,
- compute rolling features such as add volume, cancel volume, execution volume, trade imbalance, and spread-related fields.

This file should be studied before any future LOB milestone, but not copied directly.

### One-Pass Raw ITCH To Features

`extract_stock_features.py` shows a single-pass variant that reads raw multi-symbol ITCH data, filters for one symbol, and writes LOB/order-flow Parquet directly.

Useful ideas:

- avoid writing intermediate per-symbol `.itch50.gz` files when disk space matters,
- stream through the raw file once,
- keep symbol filtering separate from feature generation.

This is a promising later design, but it is more complex than the current project state.

### Feature Analysis

`feature_analysis_script.py` and `feature_analysis_part2.py` analyze LOB feature Parquet files.

Useful ideas:

- categorize feature columns,
- inspect spread and mid-price behavior,
- compute correlations,
- check redundancy,
- compare order-flow windows.

These scripts are useful only after the project can produce trusted LOB feature datasets.

### SLURM Scripts

The `.sbatch` files are useful examples of HPC job structure:

- job name,
- output/error logs,
- CPU and memory requests,
- exported parameters,
- reproducible command echoing.

They should be treated as examples only because paths, users, environments, and resource requests are professor-specific.

## Sensitive Material

One download script contains apparent plaintext Nasdaq access credentials.

Do not:

- copy that file into this repo,
- commit it,
- paste the credentials into documentation,
- share it in reports,
- use it as-is.

Raw Nasdaq data and access credentials must remain outside Git and outside shareable artifacts.

## Compatibility Notes

The professor's code is not guaranteed to work unchanged with this repo's installed MeatPy version.

One concrete compatibility risk found during inspection:

- this project's MeatPy exposes order replace fields as `original_ref` and `new_ref`,
- one attached handler appeared to use names like `orig_order_ref` and `new_order_ref`.

Any future adaptation must start with small tests around actual MeatPy message objects and field names.

## Relationship To Current Project

Current project datasets:

- `message_events`: broad generated audit dataset,
- `order_events`: focused event-level dataset derived from MeatPy order messages.

The professor's LOB files point toward a possible future dataset:

- `lob_snapshots` or `lob_features`: symbol-specific LOB state and rolling order-flow features.

That future dataset should not replace `message_events` or `order_events`.

Likely relationship:

- `message_events` proves broad raw-feed coverage,
- `order_events` proves structured order-event extraction,
- future `lob_snapshots` would prove MeatPy-based book/state processing for one symbol.

## Recommended Learning Path

Do not jump directly into full LOB reconstruction.

Recommended checkpoint order:

1. Read and explain MeatPy's existing LOB APIs in the installed environment.
2. Build a tiny synthetic MeatPy message sequence test for one symbol.
3. Use MeatPy's processor/book classes to prove one add/cancel/delete flow.
4. Write a minimal `lob_snapshots` prototype for one symbol and a very small bounded message count.
5. Add structural validation for the prototype output.
6. Only then consider an HPC run.

## Current Decision

The attachments are useful and should influence the roadmap, but no source files from the archive are imported into the project at this time.

