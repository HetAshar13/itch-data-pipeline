# Operations Runbook

This runbook explains how to operate the project safely. It is command-focused:
use it when running the pipeline, validating outputs, submitting Iris jobs, or
recovering from common failures.

## Safety Rules

- Do not commit or share raw Nasdaq ITCH `.gz` files.
- Do not commit or share large generated Parquet outputs.
- Keep raw data in ignored local storage or private Iris scratch.
- Copy back only proof artifacts: manifests, validation JSON, DuckDB summary
  JSON, SLURM `.out` / `.err`, Markdown reports, and small proof `.tar.gz`
  bundles.
- Use MeatPy for parsing/reconstruction. Do not add a custom ITCH parser.
- Keep Streamlit presentation-only; do not trigger extraction from the app.

## Local Windows Operation

Use local Windows for development, unit tests, small bounded extractions, and
report generation.

```powershell
cd D:\Downloads\itch-data-pipeline-starter\itch-data-pipeline-starter
.\.venv\Scripts\Activate.ps1
python -m pytest
python -m itch_data_pipeline.cli healthcheck
```

Raw-data safety on the active local workspace may fail if ignored `data/` or
`outputs/` exist. That is expected. To verify a public-safe package, scan a
clean copy or archive that excludes raw/generated files.

## Docker Operation

Use Docker to verify that the project runs in a clean public-safe Linux
environment.

```powershell
docker build -t itch-data-pipeline:test .
docker run --rm itch-data-pipeline:test
docker run --rm itch-data-pipeline:test python -m itch_data_pipeline.cli healthcheck
docker run --rm itch-data-pipeline:test python -m itch_data_pipeline.cli check-raw-data-safety
```

Expected current proof:

- container tests pass,
- healthcheck passes,
- raw-data safety passes with `0` violations.

## Small Local Extraction

Use this only when a private local ITCH file exists under ignored `data/`.

```powershell
python -m itch_data_pipeline.cli extract-itch50-sample --input data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz --date 2019-12-30 --max-messages 100000 --output-root outputs\local
python -m itch_data_pipeline.cli validate-message-events --output-root outputs\local --date 2019-12-30
python -m itch_data_pipeline.cli query-message-types --output-root outputs\local --date 2019-12-30 --limit 10
```

For local LOB smoke tests:

```powershell
python -m itch_data_pipeline.cli extract-lob-snapshots-sample --input data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz --date 2019-12-30 --symbol SPY --max-messages 100000 --output-root outputs\local
python -m itch_data_pipeline.cli validate-lob-snapshots --output-root outputs\local --date 2019-12-30 --symbol SPY
python -m itch_data_pipeline.cli query-lob-summary --output-root outputs\local --date 2019-12-30 --symbol SPY
```

## Iris Login And Setup

Known working login:

```powershell
ssh iris-cluster
```

Known private Iris paths:

```text
/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz
/scratch/users/hashar/itch-data-pipeline/outputs/
/scratch/users/hashar/itch-data-pipeline/reports/
/scratch/users/hashar/itch-data-pipeline/proof/
```

If login prompts for a key passphrase/password, enter it manually. If non-
interactive SSH fails, use the manual terminal workflow and bundle proof
artifacts into one `.tar.gz` before copying back.

## Iris Bounded LOB Job

Run from the project directory on Iris with the virtual environment activated.

```bash
export ITCH_INPUT=/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz
export ITCH_DATE=2019-12-30
export SYMBOL=SPY
export OUTPUT_ROOT=/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_scale10m
export MAX_MESSAGES=10000000
export SUMMARY_PATH=/scratch/users/hashar/itch-data-pipeline/reports/lob_summary_${SYMBOL}_${ITCH_DATE}_10m.json

sbatch hpc/submit_lob_snapshots.slurm
```

Monitor:

```bash
squeue -j <job_id>
tail -n 80 logs/hpc/itch_lob_snapshots_<job_id>.out
tail -n 80 logs/hpc/itch_lob_snapshots_<job_id>.err
```

If `squeue -j <job_id>` returns `Invalid job id specified`, the job likely left
the queue. Inspect the `.out` and `.err` logs.

## Iris Until-EOF LOB Job

Use this only for the final larger `SPY` proof run.

```bash
export ITCH_INPUT=/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz
export ITCH_DATE=2019-12-30
export SYMBOL=SPY
export OUTPUT_ROOT=/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof
export SUMMARY_PATH=/scratch/users/hashar/itch-data-pipeline/reports/lob_summary_SPY_2019-12-30_until_eof.json

sbatch hpc/submit_lob_snapshots_until_eof.slurm
```

Expected status fields to record:

- job id,
- node,
- run mode,
- stop reason,
- messages scanned,
- snapshot rows,
- validation status,
- rules run/failed,
- duration seconds,
- summary path,
- proof bundle path.

## Proof Bundle Copy-Back

On Iris, create a proof directory for the job and copy only small artifacts.

```bash
mkdir -p /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>

cp logs/hpc/<job_log>.out /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>/
cp logs/hpc/<job_log>.err /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>/
cp <manifest.json> /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>/
cp <validation_report.json> /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>/
cp <summary.json> /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>/

tar -czf /scratch/users/hashar/itch-data-pipeline/proof/<proof_name>.tar.gz \
  -C /scratch/users/hashar/itch-data-pipeline/proof <proof_name>
```

On Windows, copy back the bundle:

```powershell
scp iris-cluster:/scratch/users/hashar/itch-data-pipeline/proof/<proof_name>.tar.gz .\logs\
Get-Item .\logs\<proof_name>.tar.gz
```

Do not copy raw ITCH input or `part-000.parquet`.

## Common Failures

SSH fails with `Permission denied (publickey)`:

- Use `ssh iris-cluster`, not an unverified host/port command.
- If prompted, enter the key passphrase/password manually.
- If still blocked, verify local SSH alias/key setup before changing project code.

`module: command not found` on Iris:

- Use system Python or the existing project virtual environment.
- Do not depend on unavailable module-system commands.

Docker tests fail because config files are missing:

- Ensure `Dockerfile` copies `Dockerfile` and `.dockerignore` into `/app`.
- Rebuild the image after Dockerfile changes.

Raw-data safety fails locally:

- Check whether ignored `data/` or `outputs/` are present.
- For public proof, scan a clean package/archive instead of the active dev
  workspace.

Validation fails:

- Read `validation_report.json`.
- Check missing columns, row-count mismatch, sequence ordering, symbol mismatch,
  or crossed top-of-book findings.
- Do not hide failures; record the job id, logs, report path, and remediation.

