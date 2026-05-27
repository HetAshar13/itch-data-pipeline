# Reproducibility

This project separates reproducible code and environments from private market
data. Raw Nasdaq ITCH files and large generated Parquet outputs stay outside
Git, Docker images, CI artifacts, and public reports.

## Local Windows Workflow

Use the local Windows environment for day-to-day development, focused tests,
small bounded runs, and Streamlit presentation checks.

```powershell
cd D:\Downloads\itch-data-pipeline-starter\itch-data-pipeline-starter
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python -m pytest
python -m itch_data_pipeline.cli healthcheck
```

Raw ITCH data, when available locally, stays under ignored local storage such as:

```text
data\nasdaq_bx_itch\20191230.BX_ITCH_50.gz
```

Generated local Parquet outputs stay under ignored `outputs/`.

## Public-Safe Docker Workflow

Use Docker to prove that the project can run in a clean Python 3.11 Linux
environment without relying on the local Windows Python setup.

```powershell
docker build -t itch-data-pipeline:test .
docker run --rm itch-data-pipeline:test
docker run --rm itch-data-pipeline:test python -m itch_data_pipeline.cli healthcheck
docker run --rm itch-data-pipeline:test python -m itch_data_pipeline.cli check-raw-data-safety
```

The Docker image intentionally excludes:

- raw `data/`,
- generated `outputs/`,
- copied `logs/`,
- Parquet files,
- raw `.gz` files,
- local virtual environments and caches.

Verified local Docker result:

- Docker version: `29.4.3`
- Image tag: `itch-data-pipeline:test`
- Container tests: `111 passed in 7.27s`
- Container healthcheck: passed
- Container raw-data safety: passed with `0` violations

## CI Workflow

GitHub Actions uses `.github/workflows/ci.yml` to verify the public-safe repo
state on push and pull request.

CI runs:

```bash
python -m pytest
python -m itch_data_pipeline.cli healthcheck
python -m itch_data_pipeline.cli check-raw-data-safety
```

This proves three separate things:

- tests confirm pipeline behavior,
- healthcheck confirms package and CLI startup,
- raw-data safety confirms the repo is safe to share.

## Iris HPC Workflow

Use Iris HPC for real Nasdaq ITCH scale runs. Do not move raw data into Git or
Docker. Keep raw files and generated Parquet outputs in private scratch space.

Known working access pattern:

```powershell
ssh iris-cluster
scp iris-cluster:/scratch/users/hashar/itch-data-pipeline/path/to/proof.tar.gz .\logs\
```

Known private Iris layout:

```text
/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/
/scratch/users/hashar/itch-data-pipeline/outputs/
/scratch/users/hashar/itch-data-pipeline/reports/
/scratch/users/hashar/itch-data-pipeline/proof/
```

Share only proof artifacts:

- SLURM `.out` / `.err` logs,
- manifests,
- validation JSON,
- DuckDB summary JSON,
- final Markdown reports,
- small proof `.tar.gz` bundles.

Do not share raw ITCH files or large Parquet outputs.

## Current Reproducibility Proof

- Local Windows tests pass.
- CI workflow is configured for tests, healthcheck, and raw-data safety.
- Docker image builds and passes tests, healthcheck, and raw-data safety.
- Iris proof exists for bounded event extraction, bounded multi-symbol LOB
  runs, and the final `SPY` until-EOF LOB extraction.
