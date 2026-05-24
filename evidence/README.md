# Public-Safe Evidence Artifacts

This directory contains curated proof artifacts for the GitHub portfolio repo.
It is intentionally small and public-safe.

Included artifact types:

- SLURM `.out` logs showing job parameters, node, healthcheck output, row counts, and completion.
- SLURM `.err` logs showing pipeline progress messages.
- Manifest JSON files showing dataset lineage, input hash, row counts, run mode, and stop reason where available.
- Validation JSON files showing validation status, rules run, and rules failed.
- DuckDB summary JSON files showing queryable analytical outputs.

Excluded artifact types:

- no raw ITCH files,
- no Nasdaq feed `.gz` files,
- no generated `part-000.parquet` files,
- no local `outputs/` directory,
- no ignored `logs/` directory,
- no credentials or private config files.

Some copied logs and manifests contain private Iris scratch paths such as
`/scratch/users/...`. These paths identify where a job ran; they are not raw
data files and do not make the underlying licensed data public.

## Included Runs

| Directory | Purpose |
| --- | --- |
| `week6_hpc/` | Bounded `message_events` and `order_events` HPC proof from job `5386100`. |
| `week11_lob_10m/` | Bounded `10,000,000` message LOB proof for `SPY`, `QQQ`, and `IWM`. |
| `week12_lob_until_eof_5406828/` | SPY until-EOF LOB proof from job `5406828`. |

Use this directory with:

- [Portfolio Case Study](../reports/portfolio_case_study.md)
- [Final Evidence Report](../reports/final_evidence_report.md)
- [Artifact Evidence Index](../reports/artifact_evidence_index.md)
