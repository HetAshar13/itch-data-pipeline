# Week 12 Final Evidence Report

## Summary

This report consolidates the project evidence generated so far: bounded
`message_events`, `order_events`, and MeatPy-based `lob_snapshots` datasets,
with validation, DuckDB summaries, and Iris SLURM proof artifacts.

The project remains a data engineering pipeline project. It uses MeatPy for ITCH
message parsing/reconstruction and focuses on reproducible artifacts, validation,
partitioned Parquet, DuckDB analytics, and HPC execution. Raw Nasdaq data and
large Parquet outputs remain outside Git.

## Shared Lineage

- Trading date: `2019-12-30`
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Raw data policy: raw Nasdaq data is not copied into Git or public reports.
- Proof source: copied logs, manifests, validation JSON files, and DuckDB summary JSON files under `logs/`.

## Week 6 Message And Order Event Proof

| Dataset | Job ID | Node | Rows | Validation | Rules Run | Rules Failed |
| --- | --- | --- | ---: | --- | ---: | ---: |
| `message_events` | `5386100` | `iris-111` | `1000000` | passed | `4` | `0` |
| `order_events` | `5386100` | `iris-111` | `796151` | passed | `7` | `0` |

This proves the project can turn parsed ITCH messages into broad audit data and
focused order-event data, with structural validation and reproducible HPC proof.

## Week 10 Single-Symbol LOB Proof

| Symbol | Job ID | Max Messages | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| SPY | `5404108` | `2000000` | `59163` | `passed` | `8` | `0` | `99.9003%` | `300.0` |

## Week 11 Multi-Symbol LOB Proof: 2M Bound

| Symbol | Job ID | Max Messages | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| IWM | `5404169` | `2000000` | `29096` | `passed` | `8` | `0` | `97.3398%` | `300.0` |
| QQQ | `5404160` | `2000000` | `43958` | `passed` | `8` | `0` | `98.0641%` | `300.0` |
| SPY | `5404108` | `2000000` | `59163` | `passed` | `8` | `0` | `99.9003%` | `300.0` |

## Week 11 Multi-Symbol LOB Proof: 10M Bound

| Symbol | Job ID | Max Messages | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| IWM | `5404485` | `10000000` | `156647` | `passed` | `8` | `0` | `99.5059%` | `300.0` |
| QQQ | `5404299` | `10000000` | `172052` | `passed` | `8` | `0` | `99.5054%` | `300.0` |
| SPY | `5404209` | `10000000` | `206927` | `passed` | `8` | `0` | `99.9715%` | `300.0` |

The 10M comparison produced `535626` total copied-proof snapshots
across `SPY`, `QQQ`, and `IWM`, with all validation reports passing.

## Week 12 SPY Until-EOF LOB Proof

| Symbol | Job ID | Node | Run Mode | Stop Reason | Messages Scanned | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| SPY | `5406828` | `iris-111` | `until_eof` | `eof` | `29156757` | `614578` | `passed` | `8` | `0` | `99.9513%` | `200.0` |

This is the final full-file proof run for the current project scope. It shows
that the pipeline can process the available `SPY` ITCH stream until the MeatPy
reader reaches EOF, while preserving explicit stop metadata in the manifest.

## What This Proves

- The same pipeline recipe can run locally and on Iris HPC.
- MeatPy-based LOB reconstruction can be orchestrated into a reproducible data product.
- Manifests and input hashes preserve lineage.
- The final `SPY` run records whether processing stopped at EOF and how many messages were scanned.
- Validation reports make pipeline outputs inspectable.
- DuckDB summaries provide analytics over generated artifacts without a database server.
- SLURM logs provide operational proof of compute-node execution.

## Limitations

- Validation is structural plus sanity checking; it is not a proof of full market microstructure correctness.
- LOB prices are raw ITCH integer units, not normalized market display prices.
- Multi-symbol LOB comparisons are bounded by message count; only the final `SPY` run is until EOF.
- Large Parquet outputs remain on private Iris scratch storage.
- Streamlit remains a thin presentation layer over existing artifacts.

## Next Direction

The final Weeks 12-15 phase should turn this evidence into a production-ready
portfolio package: reproducibility docs, CI, Docker test container, data
contracts, operations runbook, evidence index, portfolio case study, interview
prep, and a final demo script.
