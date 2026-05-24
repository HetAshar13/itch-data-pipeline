# Update 2: MeatPy-Based LOB Pipeline Findings

## Summary

Since the last update, the pipeline has been extended from message/order-event
extraction into a MeatPy-based limit order book snapshot workflow. The pipeline
now generates symbol-specific `lob_snapshots` datasets, validates them
structurally, queries them with DuckDB, and runs through SLURM on Iris.

The main result is that the same reusable SLURM workflow successfully processed
`SPY`, `QQQ`, and `IWM` at both 2 million and 10 million message bounds. All
runs passed validation with 8 rules and 0 failures.

## 10M Message LOB Results

| Symbol | Snapshots | Two-sided snapshots | Two-sided % | Median raw spread | Validation |
| --- | ---: | ---: | ---: | ---: | --- |
| SPY | 206,927 | 206,868 | 99.97% | 300.0 | passed |
| QQQ | 172,052 | 171,201 | 99.51% | 300.0 | passed |
| IWM | 156,647 | 155,873 | 99.51% | 300.0 | passed |

## Findings Summary

- Built a MeatPy-based `lob_snapshots` pipeline without writing a custom ITCH parser.
- Added fixed top-5 bid/ask snapshot rows using raw ITCH price integers.
- Added validation for file existence, expected columns, row count, manifest match, requested symbol, sequence ordering, timestamp ordering, and non-crossed top-of-book.
- Added DuckDB summaries for snapshot count, two-sided percentage, raw spread, and level-1 imbalance.
- Ran Iris SLURM jobs for `SPY`, `QQQ`, and `IWM` at 2M and 10M message bounds.
- Copied back only proof artifacts: logs, manifests, validation reports, and summary JSON files.

## Data Governance

Raw Nasdaq data stayed outside the repository. The shareable artifacts are
reports, manifests, validation JSON files, summaries, and SLURM logs, not raw
data or large Parquet outputs.

## Key Proof Artifacts

- 2M comparison report: `reports/week11_lob_comparison.md`
- 10M comparison report: `reports/week11_lob_10m_comparison.md`
- Week 10 status: `docs/WEEK10_HPC_LOB_STATUS.md`
- Week 11 multi-symbol status: `docs/WEEK11_HPC_LOB_MULTI_SYMBOL_STATUS.md`
- Week 11 10M status: `docs/WEEK11_HPC_LOB_10M_STATUS.md`
- 10M proof directory: `logs/week11_lob_10m/`

## Next Direction

The next phase is to consolidate the project into a final portfolio-ready data
engineering package: a final report, data contracts, reproducibility
documentation, an operations runbook, CI/Docker checks, and a short
demo/interview guide. One final controlled Iris run for `SPY` until EOF is also
planned, using the same proof-artifact discipline.
