from __future__ import annotations

import re
from pathlib import Path
from typing import Any


SHAREABLE_NOTE = "Yes - copied proof artifact; no raw ITCH or Parquet output."


def _artifact_type(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".tar.gz"):
        return "proof_bundle"
    if name.endswith(".out"):
        return "slurm_stdout"
    if name.endswith(".err"):
        return "slurm_stderr"
    if "manifest" in name and name.endswith(".json"):
        return "manifest"
    if "validation" in name and name.endswith(".json"):
        return "validation_report"
    if "summary" in name and name.endswith(".json"):
        return "duckdb_summary"
    if name.endswith(".log"):
        return "local_log"
    if name.endswith(".json"):
        return "json_proof"
    return "other"


def _run_group(path: Path, proof_root: Path) -> str:
    relative = path.relative_to(proof_root)
    if len(relative.parts) > 1:
        return relative.parts[0]
    name = path.name
    if name.startswith("hpc_"):
        return "week6_hpc"
    if name.startswith("streamlit"):
        return "streamlit_smoke"
    if name.endswith(".tar.gz"):
        return name[:-7]
    if name.startswith("week"):
        return path.stem
    return "root"


def _job_id(path: Path) -> str:
    match = re.search(r"(\d{6,})", path.name)
    return match.group(1) if match else ""


def _evidence_value(artifact_type: str) -> str:
    return {
        "proof_bundle": "Bundled proof artifacts for copy-back/review.",
        "slurm_stdout": "SLURM stdout: job id, node, parameters, completion.",
        "slurm_stderr": "Pipeline logging and extraction progress.",
        "manifest": "Lineage: input path/hash, row counts, run metadata.",
        "validation_report": "Validation status, rules run, rules failed.",
        "duckdb_summary": "DuckDB analytical summary over generated Parquet.",
        "local_log": "Local app or smoke-test execution log.",
        "json_proof": "Structured copied proof JSON.",
    }.get(artifact_type, "Auxiliary copied proof artifact.")


def _is_indexed_artifact(path: Path) -> bool:
    name = path.name.lower()
    if path.is_dir():
        return False
    if name.endswith((".out", ".err", ".json", ".log", ".tar.gz")):
        return True
    return False


def collect_evidence_artifacts(proof_root: str | Path = "logs") -> list[dict[str, Any]]:
    root = Path(proof_root)
    artifacts: list[dict[str, Any]] = []

    if not root.exists():
        return artifacts

    for path in sorted(root.rglob("*")):
        if not _is_indexed_artifact(path):
            continue
        artifact_type = _artifact_type(path)
        artifacts.append(
            {
                "run_group": _run_group(path, root),
                "artifact_type": artifact_type,
                "path": path.relative_to(root).as_posix(),
                "job_id": _job_id(path),
                "evidence_value": _evidence_value(artifact_type),
                "shareable": SHAREABLE_NOTE,
            }
        )

    return artifacts


def build_artifact_evidence_index(
    proof_root: str | Path = "logs",
    report_path: str | Path = "reports/artifact_evidence_index.md",
) -> dict[str, Any]:
    proof_root = Path(proof_root)
    report_path = Path(report_path)
    artifacts = collect_evidence_artifacts(proof_root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _render_markdown(proof_root=proof_root, artifacts=artifacts),
        encoding="utf-8",
    )

    counts_by_type: dict[str, int] = {}
    for artifact in artifacts:
        artifact_type = artifact["artifact_type"]
        counts_by_type[artifact_type] = counts_by_type.get(artifact_type, 0) + 1

    return {
        "report_path": str(report_path),
        "proof_root": str(proof_root),
        "artifact_count": len(artifacts),
        "counts_by_type": counts_by_type,
    }


def _render_markdown(*, proof_root: Path, artifacts: list[dict[str, Any]]) -> str:
    table = "\n".join(
        "| {run_group} | `{artifact_type}` | `{path}` | `{job_id}` | {evidence_value} | {shareable} |".format(
            **artifact
        )
        for artifact in artifacts
    )
    if not table:
        table = "| _No copied proof artifacts found._ | | | | | |"

    return f"""# Artifact Evidence Index

## Purpose

This index makes copied proof artifacts discoverable. It maps each safe artifact
under `{proof_root}` to the run or evidence category it supports, so a reviewer
does not need to manually inspect the logs folder.

Raw Nasdaq data and large Parquet outputs are intentionally excluded. This index
contains only copied proof artifacts such as SLURM logs, manifests, validation
reports, DuckDB summaries, local smoke logs, and proof bundles.

## Summary

- Proof root: `{proof_root}`
- Indexed artifacts: `{len(artifacts)}`
- Shareability: proof artifacts listed here are intended to be public-safe, but
  raw data and `part-000.parquet` files must still remain outside Git.

## Evidence Artifacts

| Run Group | Type | Path Under Proof Root | Job ID | What It Proves | Shareable |
| --- | --- | --- | --- | --- | --- |
{table}
"""
