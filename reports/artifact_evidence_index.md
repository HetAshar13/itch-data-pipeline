# Artifact Evidence Index

## Purpose

This index makes copied proof artifacts discoverable. It maps each safe artifact
under `evidence` to the run or evidence category it supports, so a reviewer
does not need to manually inspect the logs folder.

Raw Nasdaq data and large Parquet outputs are intentionally excluded. This index
contains only copied proof artifacts such as SLURM logs, manifests, validation
reports, DuckDB summaries, local smoke logs, and proof bundles.

## Summary

- Proof root: `evidence`
- Indexed artifacts: `20`
- Shareability: proof artifacts listed here are intended to be public-safe, but
  raw data and `part-000.parquet` files must still remain outside Git.

## Evidence Artifacts

| Run Group | Type | Path Under Proof Root | Job ID | What It Proves | Shareable |
| --- | --- | --- | --- | --- | --- |
| event_pipeline_hpc | `slurm_stderr` | `event_pipeline_hpc/event_pipeline_5386100.err` | `5386100` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| event_pipeline_hpc | `slurm_stdout` | `event_pipeline_hpc/event_pipeline_5386100.out` | `5386100` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| event_pipeline_hpc | `validation_report` | `event_pipeline_hpc/hpc_message_events_validation_5386100.json` | `5386100` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| event_pipeline_hpc | `validation_report` | `event_pipeline_hpc/hpc_order_events_validation_5386100.json` | `5386100` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `slurm_stderr` | `lob_10m_multi_symbol/itch_lob_snapshots_5404209.err` | `5404209` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `slurm_stdout` | `lob_10m_multi_symbol/itch_lob_snapshots_5404209.out` | `5404209` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `manifest` | `lob_10m_multi_symbol/lob_manifest_IWM_2019-12-30_5404485.json` | `5404485` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `manifest` | `lob_10m_multi_symbol/lob_manifest_QQQ_2019-12-30_5404299.json` | `5404299` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `manifest` | `lob_10m_multi_symbol/lob_manifest_SPY_2019-12-30_5404209.json` | `5404209` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `duckdb_summary` | `lob_10m_multi_symbol/lob_summary_IWM_2019-12-30_5404485.json` | `5404485` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `duckdb_summary` | `lob_10m_multi_symbol/lob_summary_QQQ_2019-12-30_5404299.json` | `5404299` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `duckdb_summary` | `lob_10m_multi_symbol/lob_summary_SPY_2019-12-30_5404209.json` | `5404209` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `validation_report` | `lob_10m_multi_symbol/lob_validation_IWM_2019-12-30_5404485.json` | `5404485` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `validation_report` | `lob_10m_multi_symbol/lob_validation_QQQ_2019-12-30_5404299.json` | `5404299` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_10m_multi_symbol | `validation_report` | `lob_10m_multi_symbol/lob_validation_SPY_2019-12-30_5404209.json` | `5404209` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_spy_until_eof_5406828 | `slurm_stderr` | `lob_spy_until_eof_5406828/itch_lob_until_eof_5406828.err` | `5406828` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_spy_until_eof_5406828 | `slurm_stdout` | `lob_spy_until_eof_5406828/itch_lob_until_eof_5406828.out` | `5406828` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_spy_until_eof_5406828 | `manifest` | `lob_spy_until_eof_5406828/lob_manifest_SPY_2019-12-30_until_eof_5406828.json` | `5406828` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_spy_until_eof_5406828 | `duckdb_summary` | `lob_spy_until_eof_5406828/lob_summary_SPY_2019-12-30_until_eof_5406828.json` | `5406828` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| lob_spy_until_eof_5406828 | `validation_report` | `lob_spy_until_eof_5406828/lob_validation_SPY_2019-12-30_until_eof_5406828.json` | `5406828` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
