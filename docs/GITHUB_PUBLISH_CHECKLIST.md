# GitHub Publish Checklist

Use this checklist before sharing the project on a GitHub profile.

Recommended repository name: `itch-data-pipeline`

Recommended topics:

- `data-engineering`
- `market-data`
- `parquet`
- `duckdb`
- `hpc`
- `slurm`
- `docker`
- `python`

## 1. Verify The Public Story

- Read `README.md` as the landing page.
- Read `reports/portfolio_case_study.md` as the recruiter/engineer case study.
- Confirm the README links to:
  - `reports/portfolio_case_study.md`
  - `reports/final_evidence_report.md`
  - `docs/DATA_CONTRACTS.md`
  - `docs/OPERATIONS_RUNBOOK.md`
  - `docs/REPRODUCIBILITY.md`
  - `evidence/README.md`
  - `reports/lob_10m_comparison.md`

## 2. Run Local Verification

From PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m itch_data_pipeline.cli healthcheck
.\.venv\Scripts\python.exe -m itch_data_pipeline.cli check-raw-data-safety
```

Important: `check-raw-data-safety` may fail in the active development workspace
because ignored local `data/` and `outputs/` folders are present. That is
acceptable locally, but those files must not be staged or pushed.

## 3. Inspect What Git Would Publish

The current project folder may not be a Git repository yet. If it is already a
repo, inspect status first:

```powershell
git status --short
```

If it is not a repo, initialize it only after verifying the ignore rules:

```powershell
git init
git status --short
```

Confirm these are not staged:

- `data/`
- `outputs/`
- `logs/`
- `.venv/`
- `*.parquet`
- raw Nasdaq `*.gz` files
- private configs such as `configs/local.yaml`

The curated public evidence should come from `evidence/`, not ignored `logs/`.

## 4. Make The First Commit

```powershell
git add README.md pyproject.toml requirements.txt Dockerfile .dockerignore .gitignore
git add src tests app hpc configs docs reports evidence analytics examples data_fixtures
git status --short
git commit -m "Prepare public-safe market data engineering portfolio"
```

Before committing, inspect `git status --short` manually. If raw data,
generated Parquet, `.venv`, or ignored logs appear, stop and fix the ignore or
staging mistake first.

## 5. Create And Push The GitHub Repo

Create a public GitHub repository named `itch-data-pipeline`, then connect and
push:

```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/itch-data-pipeline.git
git push -u origin main
```

After push:

- confirm GitHub Actions CI runs,
- confirm README renders correctly,
- add the recommended repository topics,
- pin the repository on the GitHub profile,
- optionally add the project to the CV with the final concise bullet points.

## 6. Final Safety Review

On GitHub, verify:

- no raw Nasdaq files are visible,
- no generated Parquet files are visible,
- `evidence/` contains only public-safe copied proof artifacts,
- CI is visible and green,
- limitations are clearly stated in README and the portfolio case study.
