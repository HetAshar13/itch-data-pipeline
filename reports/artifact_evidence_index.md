# Artifact Evidence Index

## Purpose

This index makes copied proof artifacts discoverable. It maps each safe artifact
under `logs` to the run or evidence category it supports, so a reviewer
does not need to manually inspect the logs folder.

Raw Nasdaq data and large Parquet outputs are intentionally excluded. This index
contains only copied proof artifacts such as SLURM logs, manifests, validation
reports, DuckDB summaries, local smoke logs, and proof bundles.

## Summary

- Proof root: `logs`
- Indexed artifacts: `52`
- Shareability: proof artifacts listed here are intended to be public-safe, but
  raw data and `part-000.parquet` files must still remain outside Git.

## Evidence Artifacts

| Run Group | Type | Path Under Proof Root | Job ID | What It Proves | Shareable |
| --- | --- | --- | --- | --- | --- |
| week6_hpc | `validation_report` | `hpc_message_events_validation_5386100.json` | `5386100` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week6_hpc | `validation_report` | `hpc_order_events_validation_5386100.json` | `5386100` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week6_hpc | `slurm_stderr` | `hpc_week6_5386100.err` | `5386100` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week6_hpc | `slurm_stdout` | `hpc_week6_5386100.out` | `5386100` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| streamlit_smoke | `local_log` | `streamlit-local.err.log` | `` | Local app or smoke-test execution log. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| streamlit_smoke | `local_log` | `streamlit-local.out.log` | `` | Local app or smoke-test execution log. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| streamlit_smoke | `local_log` | `streamlit-smoke.err.log` | `` | Local app or smoke-test execution log. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| streamlit_smoke | `local_log` | `streamlit-smoke.out.log` | `` | Local app or smoke-test execution log. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week10_lob_5404108 | `slurm_stderr` | `week10_lob_5404108/itch_lob_snapshots_5404108.err` | `5404108` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week10_lob_5404108 | `slurm_stdout` | `week10_lob_5404108/itch_lob_snapshots_5404108.out` | `5404108` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week10_lob_5404108 | `manifest` | `week10_lob_5404108/lob_manifest_SPY_2019-12-30_5404108.json` | `5404108` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week10_lob_5404108 | `duckdb_summary` | `week10_lob_5404108/lob_summary_SPY_2019-12-30_5404108.json` | `5404108` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week10_lob_5404108 | `validation_report` | `week10_lob_5404108/lob_validation_SPY_2019-12-30_5404108.json` | `5404108` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week10_lob_5404108 | `proof_bundle` | `week10_lob_5404108.tar.gz` | `5404108` | Bundled proof artifacts for copy-back/review. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `slurm_stderr` | `week11_lob_10m/itch_lob_snapshots_5404209.err` | `5404209` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `slurm_stdout` | `week11_lob_10m/itch_lob_snapshots_5404209.out` | `5404209` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `slurm_stderr` | `week11_lob_10m/itch_lob_snapshots_5404299.err` | `5404299` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `slurm_stdout` | `week11_lob_10m/itch_lob_snapshots_5404299.out` | `5404299` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `slurm_stderr` | `week11_lob_10m/itch_lob_snapshots_5404485.err` | `5404485` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `slurm_stdout` | `week11_lob_10m/itch_lob_snapshots_5404485.out` | `5404485` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `manifest` | `week11_lob_10m/lob_manifest_IWM_2019-12-30_5404485.json` | `5404485` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `manifest` | `week11_lob_10m/lob_manifest_QQQ_2019-12-30_5404299.json` | `5404299` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `manifest` | `week11_lob_10m/lob_manifest_SPY_2019-12-30_5404209.json` | `5404209` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `duckdb_summary` | `week11_lob_10m/lob_summary_IWM_2019-12-30_5404485.json` | `5404485` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `duckdb_summary` | `week11_lob_10m/lob_summary_QQQ_2019-12-30_5404299.json` | `5404299` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `duckdb_summary` | `week11_lob_10m/lob_summary_SPY_2019-12-30_5404209.json` | `5404209` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `validation_report` | `week11_lob_10m/lob_validation_IWM_2019-12-30_5404485.json` | `5404485` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `validation_report` | `week11_lob_10m/lob_validation_QQQ_2019-12-30_5404299.json` | `5404299` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `validation_report` | `week11_lob_10m/lob_validation_SPY_2019-12-30_5404209.json` | `5404209` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_10m | `proof_bundle` | `week11_lob_10m.tar.gz` | `` | Bundled proof artifacts for copy-back/review. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `slurm_stderr` | `week11_lob_2m/itch_lob_snapshots_5404108.err` | `5404108` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `slurm_stdout` | `week11_lob_2m/itch_lob_snapshots_5404108.out` | `5404108` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `slurm_stderr` | `week11_lob_2m/itch_lob_snapshots_5404160.err` | `5404160` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `slurm_stdout` | `week11_lob_2m/itch_lob_snapshots_5404160.out` | `5404160` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `slurm_stderr` | `week11_lob_2m/itch_lob_snapshots_5404169.err` | `5404169` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `slurm_stdout` | `week11_lob_2m/itch_lob_snapshots_5404169.out` | `5404169` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `manifest` | `week11_lob_2m/lob_manifest_IWM_2019-12-30_5404169.json` | `5404169` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `manifest` | `week11_lob_2m/lob_manifest_QQQ_2019-12-30_5404160.json` | `5404160` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `manifest` | `week11_lob_2m/lob_manifest_SPY_2019-12-30_5404108.json` | `5404108` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `duckdb_summary` | `week11_lob_2m/lob_summary_IWM_2019-12-30_5404169.json` | `5404169` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `duckdb_summary` | `week11_lob_2m/lob_summary_QQQ_2019-12-30_5404160.json` | `5404160` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `duckdb_summary` | `week11_lob_2m/lob_summary_SPY_2019-12-30_5404108.json` | `5404108` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `validation_report` | `week11_lob_2m/lob_validation_IWM_2019-12-30_5404169.json` | `5404169` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `validation_report` | `week11_lob_2m/lob_validation_QQQ_2019-12-30_5404160.json` | `5404160` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `validation_report` | `week11_lob_2m/lob_validation_SPY_2019-12-30_5404108.json` | `5404108` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week11_lob_2m | `proof_bundle` | `week11_lob_2m.tar.gz` | `` | Bundled proof artifacts for copy-back/review. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week12_lob_until_eof_5406828 | `slurm_stderr` | `week12_lob_until_eof_5406828/itch_lob_until_eof_5406828.err` | `5406828` | Pipeline logging and extraction progress. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week12_lob_until_eof_5406828 | `slurm_stdout` | `week12_lob_until_eof_5406828/itch_lob_until_eof_5406828.out` | `5406828` | SLURM stdout: job id, node, parameters, completion. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week12_lob_until_eof_5406828 | `manifest` | `week12_lob_until_eof_5406828/lob_manifest_SPY_2019-12-30_until_eof_5406828.json` | `5406828` | Lineage: input path/hash, row counts, run metadata. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week12_lob_until_eof_5406828 | `duckdb_summary` | `week12_lob_until_eof_5406828/lob_summary_SPY_2019-12-30_until_eof_5406828.json` | `5406828` | DuckDB analytical summary over generated Parquet. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week12_lob_until_eof_5406828 | `validation_report` | `week12_lob_until_eof_5406828/lob_validation_SPY_2019-12-30_until_eof_5406828.json` | `5406828` | Validation status, rules run, rules failed. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
| week12_lob_until_eof_5406828 | `proof_bundle` | `week12_lob_until_eof_5406828.tar.gz` | `5406828` | Bundled proof artifacts for copy-back/review. | Yes - copied proof artifact; no raw ITCH or Parquet output. |
