# Week 12 HPC LOB Until-EOF Status

## Purpose

Run one final Iris proof for `SPY` using the MeatPy-based `lob_snapshots`
pipeline until the ITCH reader reaches EOF, not a fixed message bound.

This is a private/professor evidence run. Do not copy raw Nasdaq data or large
Parquet outputs into Git. Copy back only small proof artifacts.

## Target Run

- Cluster: Iris
- Symbol: `SPY`
- Date: `2019-12-30`
- Run mode: `until_eof`
- Input path on Iris:
  `/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz`
- Output root on Iris:
  `/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof`
- Summary path on Iris:
  `/scratch/users/hashar/itch-data-pipeline/reports/lob_summary_SPY_2019-12-30_until_eof.json`
- SLURM script:
  `hpc/submit_lob_snapshots_until_eof.slurm`

## Submit Commands On Iris

Run these inside the updated project directory on Iris:

```bash
cd /scratch/users/hashar/itch-data-pipeline/itch-data-pipeline-starter-new
source .venv/bin/activate

export ITCH_INPUT=/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz
export ITCH_DATE=2019-12-30
export SYMBOL=SPY
export OUTPUT_ROOT=/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof
export SUMMARY_PATH=/scratch/users/hashar/itch-data-pipeline/reports/lob_summary_SPY_2019-12-30_until_eof.json

sbatch hpc/submit_lob_snapshots_until_eof.slurm
```

Recorded job id:

```text
Job ID: 5406828
```

## Monitor Commands On Iris

Replace `<job_id>` with the submitted job id:

```bash
squeue -j <job_id>
tail -n 80 logs/hpc/itch_lob_until_eof_<job_id>.out
tail -n 80 logs/hpc/itch_lob_until_eof_<job_id>.err
```

If `squeue -j <job_id>` later says `Invalid job id specified`, that usually
means the job left the queue. Then inspect the `.out` and `.err` files.

## Expected Proof Artifacts On Iris

Do copy these:

- `logs/hpc/itch_lob_until_eof_<job_id>.out`
- `logs/hpc/itch_lob_until_eof_<job_id>.err`
- manifest JSON from:
  `/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/manifest.json`
- validation JSON from:
  `/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/validation_report.json`
- summary JSON from:
  `/scratch/users/hashar/itch-data-pipeline/reports/lob_summary_SPY_2019-12-30_until_eof.json`

Do not copy these:

- raw ITCH input `.gz`
- large `part-000.parquet`
- `.venv`
- package caches

## Proof Bundle Commands On Iris

After the job finishes, replace `<job_id>` and run:

```bash
mkdir -p /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>

cp logs/hpc/itch_lob_until_eof_<job_id>.out \
  /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>/

cp logs/hpc/itch_lob_until_eof_<job_id>.err \
  /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>/

cp /scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/manifest.json \
  /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>/lob_manifest_SPY_2019-12-30_until_eof_<job_id>.json

cp /scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/validation_report.json \
  /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>/lob_validation_SPY_2019-12-30_until_eof_<job_id>.json

cp /scratch/users/hashar/itch-data-pipeline/reports/lob_summary_SPY_2019-12-30_until_eof.json \
  /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>/lob_summary_SPY_2019-12-30_until_eof_<job_id>.json

tar -czf /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>.tar.gz \
  -C /scratch/users/hashar/itch-data-pipeline/proof week12_lob_until_eof_<job_id>

ls -lh /scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>.tar.gz
```

## Copy-Back Command On Windows

Run from local PowerShell in the repo root:

```powershell
scp iris-cluster:/scratch/users/hashar/itch-data-pipeline/proof/week12_lob_until_eof_<job_id>.tar.gz .\logs\
Get-Item .\logs\week12_lob_until_eof_<job_id>.tar.gz
```

## Status Fields To Record After Completion

```text
Job ID: 5406828
Node: iris-111
Run mode: until_eof
Stop reason: eof
Messages scanned: 29156757
Snapshot rows: 614578
Validation status: passed
Rules run: 8
Rules failed: 0
Duration seconds: 3296.740014
Summary path: /scratch/users/hashar/itch-data-pipeline/reports/lob_summary_SPY_2019-12-30_until_eof.json
Proof bundle: logs/week12_lob_until_eof_5406828.tar.gz
```
