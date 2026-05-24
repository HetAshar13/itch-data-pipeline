# Week 10 HPC LOB Status

## Current Status

The first bounded Iris LOB snapshot run succeeded.

## Access Pattern That Worked

Use the local SSH alias:

```powershell
ssh iris-cluster
```

This alias uses:

- host: `access-iris.uni.lu`
- port: `8022`
- user: `hashar`
- identity file: `~/.ssh/ulhpc_ed25519`

The login prompts for the SSH key passphrase/password. For file transfer, use
the same alias:

```powershell
scp local-file iris-cluster:/scratch/users/hashar/itch-data-pipeline/
```

To avoid repeated prompts when copying proof files back, bundle proof files on
Iris first and copy one small `.tar.gz` archive.

## Completed Iris Test Step

Before submitting the LOB SLURM job, the updated Week 10 code was unpacked into:

```text
/scratch/users/hashar/itch-data-pipeline/itch-data-pipeline-starter-new
```

The Iris virtual environment used Python `3.11.13`.

The full test suite passed on Iris:

```text
81 passed in 4.23s
```

## Completed SLURM Run

- Job ID: `5404108`
- Compute node: `iris-111`
- Dataset: `lob_snapshots`
- Date: `2019-12-30`
- Symbol: `SPY`
- Message scan bound: `2000000`
- Snapshot depth: `5`
- Input path: `/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz`
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Output root: `/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_week10`
- `lob_snapshots` rows: `59163`
- Validation status: `passed`
- Validation rules run: `8`
- Validation rules failed: `0`

## DuckDB Summary

- Snapshot count: `59163`
- Two-sided snapshots: `59104`
- Two-sided snapshot percent: `99.9002755100316`
- Median raw spread: `300.0`
- Average raw spread: `351.1166756903086`
- Minimum raw spread: `100`
- Maximum raw spread: `6000`
- Average level-1 imbalance: `-0.036631156986337975`
- First timestamp ns: `25204435833095`
- Last timestamp ns: `34826658964471`

## Local Proof Artifacts

Small proof artifacts were copied back locally under:

```text
logs/week10_lob_5404108/
```

Files:

- `itch_lob_snapshots_5404108.out`
- `itch_lob_snapshots_5404108.err`
- `lob_manifest_SPY_2019-12-30_5404108.json`
- `lob_validation_SPY_2019-12-30_5404108.json`
- `lob_summary_SPY_2019-12-30_5404108.json`

The copied archive is:

```text
logs/week10_lob_5404108.tar.gz
```

No raw Nasdaq data or large Parquet files were copied into the repo.

## Learning Takeaway

Local tests prove the code path. Iris tests prove the same code works in the
target environment. The SLURM run proves the pipeline can process private raw
ITCH data on a compute node and produce validation plus analytics artifacts
without copying raw data into Git.

