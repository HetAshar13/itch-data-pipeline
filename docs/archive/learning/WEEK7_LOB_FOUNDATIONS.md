# Week 7 LOB Foundations

## Goal

Week 7 starts the LOB phase without building the full LOB pipeline yet.

The goal is to prove, with tiny synthetic message sequences, that the installed MeatPy package can update a limit order book for one symbol. This keeps the learning focused before using large real Nasdaq files.

## What MeatPy Provides

MeatPy already provides the core order-book mechanics:

- `ITCH50MarketProcessor` routes parsed ITCH message objects into book updates for one target instrument.
- `LimitOrderBook` stores bid and ask levels and order queues.
- Add, cancel, delete, replace, and execute messages are handled by MeatPy classes.

This project should not reimplement those mechanics. The project should orchestrate bounded runs, write Parquet datasets, write manifests, validate outputs, query artifacts, and produce reports.

## What The Synthetic Tests Prove

The Week 7 tests use actual MeatPy message classes:

- an add message creates a bid level for the target symbol,
- an add message for a different symbol is ignored,
- a cancel message reduces the existing order volume,
- a replace message changes order reference, price, and volume,
- a delete message removes the order from the book.

This is intentionally small. It proves the installed MeatPy APIs are usable before the project adds a `lob_snapshots` dataset.

## What This Does Not Prove

These tests do not prove full market microstructure correctness.

They also do not prove:

- behavior on all ITCH message types,
- behavior on the full Nasdaq file,
- correctness of future Parquet schema design,
- correctness of future HPC execution.

Those belong to later checkpoints.

## Learning Checkpoint

Question:

Why is a tiny synthetic LOB sequence safer than starting with the full raw ITCH file?

Strong answer:

A tiny synthetic sequence isolates one concept at a time. If add, cancel, replace, or delete behavior fails, the failure is easy to understand. With a full raw ITCH file, many message types, symbols, timestamps, and market-state transitions interact at once, so debugging becomes much harder.

## Next Step

The next checkpoint is Week 8: design the minimal `lob_snapshots` row mapping and extraction path for one symbol, fixed top-5 depth, raw price integers, and a bounded message scan.

