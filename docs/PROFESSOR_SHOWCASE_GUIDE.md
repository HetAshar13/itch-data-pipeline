# Professor Showcase Guide

This guide is for a private technical review with a professor who already has
access to the licensed Nasdaq ITCH data. Use the public GitHub repository for
the polished project story, then use local/private evidence artifacts to show
the stronger reproducibility and HPC proof.

The core message:

> MeatPy handles ITCH parsing and LOB reconstruction. This project builds the
> data engineering layer around it: bounded and until-EOF execution,
> partitioned Parquet datasets, manifests, input hashes, validation reports,
> DuckDB summaries, Iris SLURM proof, Docker/CI reproducibility, and
> public-safe evidence.

Do not present this as a trading strategy, prediction system, or custom ITCH
parser. Present it as a reliable market-data engineering pipeline.

## Files To Open Before The Meeting

Open these in advance so the walkthrough is smooth:

- GitHub repository: `https://github.com/HetAshar13/itch-data-pipeline`
- `reports/final_evidence_report.md`
- `reports/portfolio_case_study.md`
- `reports/lob_10m_comparison.md`
- `evidence/README.md`
- `docs/DATA_CONTRACTS.md`
- `docs/OPERATIONS_RUNBOOK.md`

Keep the raw Nasdaq `.gz` file, large Parquet outputs, credentials, and private
configs out of the meeting artifacts unless the professor explicitly asks to
inspect them on Iris.

## 15-Minute Walkthrough

### 1. Project Goal

Say:

> Nasdaq ITCH is high-volume binary market data, not a ready analytics table.
> The goal was to build a reliable data engineering pipeline that turns parsed
> ITCH messages and reconstructed LOB state into validated, queryable,
> reproducible artifacts.

Then clarify:

> I did not write a custom parser. MeatPy is used for protocol parsing and LOB
> reconstruction. The project is about the engineering layer around that.

### 2. Public GitHub Repo

Open the GitHub README and show:

- proof table,
- architecture diagram,
- CI badge,
- Docker and reproducibility section,
- public-safety policy,
- limitations.

Say:

> This is the public-safe portfolio version. It excludes raw Nasdaq data and
> large Parquet outputs, but includes code, tests, docs, reports, and curated
> proof artifacts.

### 3. Architecture

Use this simple flow:

```text
Private Nasdaq ITCH .gz
     -> MeatPy parsing / LOB reconstruction
     -> pipeline runners
     -> message_events, order_events, lob_snapshots
     -> Parquet + manifest + validation JSON
     -> DuckDB summaries
     -> reports / evidence / Streamlit presentation
```

Key point:

> The pipeline separates domain parsing from data engineering responsibilities.

### 4. Data Products

Explain the three datasets:

- `message_events`: broad audit dataset from parsed MeatPy messages.
- `order_events`: focused add, cancel, delete, replace, and execute event dataset.
- `lob_snapshots`: symbol-specific top-5 bid/ask LOB state after MeatPy applies
  book-changing events.

Important distinction:

> `order_events` tells us what happened. `lob_snapshots` tells us what the
> reconstructed book looked like after those events.

### 5. Final Evidence Report

Open `reports/final_evidence_report.md` and highlight:

- `1,000,000` message-event rows,
- `796,151` order-event rows,
- `535,626` total 10M multi-symbol LOB snapshots,
- `29,156,757` SPY messages scanned until EOF,
- `614,578` SPY LOB snapshots,
- all validation reports passed.

### 6. 10M Multi-Symbol Comparison

Open `reports/lob_10m_comparison.md`.

Say:

> I first proved one symbol, then held the run recipe stable and compared SPY,
> QQQ, and IWM at the same 10M message bound. That isolates symbol differences
> from pipeline changes.

Highlight:

- SPY: `206,927` snapshots,
- QQQ: `172,052` snapshots,
- IWM: `156,647` snapshots,
- total: `535,626` snapshots,
- all validation reports passed.

### 7. Strongest HPC Proof

Open `evidence/README.md`, then show the SPY until-EOF evidence directory.

Say:

> The strongest proof is the SPY until-EOF SLURM job. It scanned `29,156,757`
> messages, stopped because the reader reached EOF, produced `614,578`
> snapshots, and passed validation.

Mention:

- job ID: `5406828`,
- node: `iris-111`,
- stop reason: `eof`.

### 8. Validation Boundaries

Open `docs/DATA_CONTRACTS.md`.

Say:

> Validation checks structure and sanity: expected columns, positive row counts,
> manifest-to-Parquet row-count consistency, sequence ordering, timestamp
> ordering, symbol consistency, and no crossed top-of-book where both sides
> exist.

Then say clearly:

> This does not prove full market microstructure correctness. It proves the
> generated artifacts are structurally consistent and safe to analyze.

### 9. Private Reproducibility On Iris

Open `docs/OPERATIONS_RUNBOOK.md`.

Say:

> The pipeline can be rerun on Iris using the same code and licensed raw data
> access. The raw file itself is not in GitHub; the run is parameterized through
> SLURM and records the input hash, output root, job ID, validation status, and
> summary path.

Do not rerun a heavy job live unless the professor explicitly asks. Prefer
showing the reproducible command pattern and the completed logs.

### 10. Streamlit

If shown, keep it brief:

> Streamlit is only a presentation layer. It reads existing artifacts and does
> not run extraction, validation, analytics, or raw ITCH access.

## Exact Results To Mention

| Area | Proof |
| --- | --- |
| Message events | Job `5386100`, `1,000,000` rows, validation passed |
| Order events | Job `5386100`, `796,151` rows, validation passed |
| SPY 10M LOB | Job `5404209`, `206,927` snapshots, validation passed |
| QQQ 10M LOB | Job `5404299`, `172,052` snapshots, validation passed |
| IWM 10M LOB | Job `5404485`, `156,647` snapshots, validation passed |
| 10M multi-symbol total | `535,626` snapshots |
| SPY until EOF | Job `5406828`, `29,156,757` messages scanned, `614,578` snapshots |
| Engineering quality | `126` local tests, Docker runtime, GitHub Actions CI |

## Questions To Be Ready For

**What did you build beyond MeatPy?**

> MeatPy gives the project the domain engine: ITCH parsing and LOB
> reconstruction. I built the data engineering system around it. That includes
> extraction runners, stable Parquet schemas, partitioned output layout,
> manifests, input SHA-256 lineage, validation reports, DuckDB analytics, SLURM
> execution, copied proof artifacts, Docker/CI reproducibility, and public-safe
> documentation.

**Why is this useful?**

> The value is reliability and reproducibility. The project turns licensed
> binary market data into validated, queryable artifacts with traceable lineage
> and HPC execution proof. That is the kind of engineering needed before any
> serious downstream analysis can be trusted.

**What does validation prove?**

> It proves structural consistency and sanity checks. It does not prove complete
> exchange-level correctness or trading correctness.

**Why DuckDB?**

> DuckDB queries Parquet directly, so analytics stay lightweight and
> reproducible without a database server or warehouse dependency.

**Why keep prices raw?**

> The project stores ITCH prices as raw integer units to avoid claiming price
> normalization work that was not part of the validated pipeline.

## What Not To Do

- Do not present this as a trading strategy.
- Do not claim market prediction or alpha.
- Do not claim validation proves complete exchange correctness.
- Do not send raw `.gz` ITCH files through email or GitHub.
- Do not make Streamlit the centerpiece.
- Do not over-focus on week numbers; present it as one complete pipeline.

## Recommended Closing

Say:

> The project is now a public-safe but technically complete data engineering
> case study. It demonstrates reliable processing of licensed ITCH data using
> MeatPy, validated Parquet datasets, DuckDB summaries, Iris SLURM execution,
> and reproducible evidence. I would like your feedback on whether the strongest
> next academic direction would be deeper LOB correctness validation, more dates
> and symbols, or performance profiling.
