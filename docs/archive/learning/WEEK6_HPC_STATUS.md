# Week 6 HPC Status

## Current Status

Iris is the target cluster for the Week 6 professor-ready run.

Host-key verification was repaired safely:

- Official ULHPC SSH docs list the Iris ED25519 fingerprint as `SHA256:tkhRD9IVo04NPw4OV/s2LSKEwe54LAEphm7yx8nq1pE`.
- A local `ssh-keyscan` for `[access-iris.uni.lu]:8022` returned the same fingerprint.
- The verified host key was added to `~/.ssh/known_hosts`.

SSH access was completed manually with password/passphrase prompts, and the bounded Week 6 SLURM run succeeded.

## Completed SLURM Run

- Job ID: `5386100`
- Compute node: `iris-111`
- Input: private Nasdaq BX ITCH sample under `/scratch/users/hashar/itch-data-pipeline/data/`
- Message scan bound: `1000000`
- `message_events` rows: `1000000`
- `order_events` rows: `796151`
- `message_events` validation: `4` rules run, `0` failed
- `order_events` validation: `7` rules run, `0` failed
- Report: `/scratch/users/hashar/itch-data-pipeline/reports/week6_showcase.md`

Copied local proof artifacts:

- `reports/week6_showcase_hpc.md`
- `logs/hpc_week6_5386100.out`
- `logs/hpc_week6_5386100.err`
- `logs/hpc_message_events_validation_5386100.json`
- `logs/hpc_order_events_validation_5386100.json`

## Week 6 SLURM Job

To rerun on Iris:

```bash
cd /scratch/users/hashar/itch-data-pipeline/itch-data-pipeline-starter
source .venv/bin/activate

export ITCH_INPUT=/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz
export ITCH_DATE=2019-12-30
export OUTPUT_ROOT=/scratch/users/hashar/itch-data-pipeline/outputs/hpc
export MAX_MESSAGES=1000000
export REPORT_PATH=/scratch/users/hashar/itch-data-pipeline/reports/week6_showcase.md

sbatch hpc/submit_week6_showcase.slurm
```

Do not copy raw Nasdaq data into Git. Copy back only reports, manifests, validation JSON files, and logs.

## Access Note

Automated non-interactive SSH still may fail if the key passphrase/password is required. For fewer repeated prompts, use `ssh-agent` locally or bundle proof files into one archive before copying.
