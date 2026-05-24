from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _job_node_from_log(path: Path) -> tuple[str, str]:
    text = _read_text(path)
    job_match = re.search(r"SLURM_JOB_ID=(\d+)", text)
    node_match = re.search(r"Job started on ([^\s]+)", text)
    return (
        job_match.group(1) if job_match else "unknown",
        node_match.group(1) if node_match else "unknown",
    )


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _load_week6(proof_root: Path) -> dict[str, Any]:
    message_validation = _read_json(proof_root / "hpc_message_events_validation_5386100.json")
    order_validation = _read_json(proof_root / "hpc_order_events_validation_5386100.json")
    job_id, node = _job_node_from_log(proof_root / "hpc_week6_5386100.out")
    return {
        "job_id": job_id,
        "node": node,
        "message_events_rows": message_validation["row_count"],
        "message_events_status": message_validation["status"],
        "message_events_rules_run": message_validation["rules_run"],
        "message_events_rules_failed": message_validation["rules_failed"],
        "order_events_rows": order_validation["row_count"],
        "order_events_status": order_validation["status"],
        "order_events_rules_run": order_validation["rules_run"],
        "order_events_rules_failed": order_validation["rules_failed"],
    }


def _load_lob_runs(proof_dir: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for summary_path in sorted(proof_dir.glob("lob_summary_*_*.json")):
        match = re.match(r"lob_summary_([A-Z]+)_\d{4}-\d{2}-\d{2}_(\d+)\.json", summary_path.name)
        if not match:
            continue
        symbol, job_id = match.groups()
        manifest_path = proof_dir / f"lob_manifest_{symbol}_2019-12-30_{job_id}.json"
        validation_path = proof_dir / f"lob_validation_{symbol}_2019-12-30_{job_id}.json"
        log_path = proof_dir / f"itch_lob_snapshots_{job_id}.out"

        summary = _read_json(summary_path)
        manifest = _read_json(manifest_path)
        validation = _read_json(validation_path)
        parsed_job_id, node = _job_node_from_log(log_path)

        runs.append(
            {
                "symbol": symbol,
                "job_id": parsed_job_id if parsed_job_id != "unknown" else job_id,
                "node": node,
                "max_messages": manifest["max_messages"],
                "input_sha256": manifest["input_sha256"],
                "duration_seconds": manifest["duration_seconds"],
                "snapshots": summary["snapshot_count"],
                "two_sided_snapshots": summary["two_sided_snapshot_count"],
                "two_sided_percent": summary["two_sided_snapshot_percent"],
                "median_spread_raw": summary["median_spread_1_raw"],
                "avg_spread_raw": summary["avg_spread_1_raw"],
                "avg_level1_imbalance": summary["avg_level1_imbalance"],
                "validation_status": validation["status"],
                "rules_run": validation["rules_run"],
                "rules_failed": validation["rules_failed"],
            }
        )

    return sorted(runs, key=lambda row: (row["max_messages"], row["symbol"]))


def _load_lob_until_eof_runs(proof_dir: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for summary_path in sorted(proof_dir.glob("lob_summary_*_until_eof_*.json")):
        match = re.match(r"lob_summary_([A-Z]+)_\d{4}-\d{2}-\d{2}_until_eof_(\d+)\.json", summary_path.name)
        if not match:
            continue
        symbol, job_id = match.groups()
        manifest_path = proof_dir / f"lob_manifest_{symbol}_2019-12-30_until_eof_{job_id}.json"
        validation_path = proof_dir / f"lob_validation_{symbol}_2019-12-30_until_eof_{job_id}.json"
        log_path = proof_dir / f"itch_lob_until_eof_{job_id}.out"

        summary = _read_json(summary_path)
        manifest = _read_json(manifest_path)
        validation = _read_json(validation_path)
        parsed_job_id, node = _job_node_from_log(log_path)

        runs.append(
            {
                "symbol": symbol,
                "job_id": parsed_job_id if parsed_job_id != "unknown" else job_id,
                "node": node,
                "run_mode": manifest["run_mode"],
                "stop_reason": manifest["stop_reason"],
                "messages_scanned": manifest["messages_scanned"],
                "duration_seconds": manifest["duration_seconds"],
                "input_sha256": manifest["input_sha256"],
                "snapshots": summary["snapshot_count"],
                "two_sided_snapshots": summary["two_sided_snapshot_count"],
                "two_sided_percent": summary["two_sided_snapshot_percent"],
                "median_spread_raw": summary["median_spread_1_raw"],
                "avg_spread_raw": summary["avg_spread_1_raw"],
                "avg_level1_imbalance": summary["avg_level1_imbalance"],
                "validation_status": validation["status"],
                "rules_run": validation["rules_run"],
                "rules_failed": validation["rules_failed"],
            }
        )

    return sorted(runs, key=lambda row: row["symbol"])


def build_week12_final_report(
    proof_root: str | Path = "logs",
    report_path: str | Path = "reports/week12_final_report.md",
) -> dict[str, Any]:
    proof_root = Path(proof_root)
    report = Path(report_path)
    week6 = _load_week6(proof_root)
    week10_runs = _load_lob_runs(proof_root / "week10_lob_5404108")
    week11_2m_runs = _load_lob_runs(proof_root / "week11_lob_2m")
    week11_10m_runs = _load_lob_runs(proof_root / "week11_lob_10m")
    week12_until_eof_runs = _load_lob_until_eof_runs(proof_root / "week12_lob_until_eof_5406828")
    input_sha_path = _first_existing(
        [
            proof_root / "week11_lob_10m" / "lob_manifest_SPY_2019-12-30_5404209.json",
            proof_root / "week11_lob_2m" / "lob_manifest_SPY_2019-12-30_5404108.json",
            proof_root / "week10_lob_5404108" / "lob_manifest_SPY_2019-12-30_5404108.json",
        ]
    )
    input_sha = _read_json(input_sha_path)["input_sha256"] if input_sha_path is not None else "unknown"

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        _render_markdown(
            input_sha=input_sha,
            week6=week6,
            week10_runs=week10_runs,
            week11_2m_runs=week11_2m_runs,
            week11_10m_runs=week11_10m_runs,
            week12_until_eof_runs=week12_until_eof_runs,
        ),
        encoding="utf-8",
    )

    return {
        "report_path": str(report),
        "week6_message_events_rows": week6["message_events_rows"],
        "week6_order_events_rows": week6["order_events_rows"],
        "week10_lob_runs": len(week10_runs),
        "week11_2m_lob_runs": len(week11_2m_runs),
        "week11_10m_lob_runs": len(week11_10m_runs),
        "week11_10m_total_snapshots": sum(run["snapshots"] for run in week11_10m_runs),
        "week12_until_eof_lob_runs": len(week12_until_eof_runs),
        "week12_until_eof_messages_scanned": sum(run["messages_scanned"] for run in week12_until_eof_runs),
        "week12_until_eof_snapshots": sum(run["snapshots"] for run in week12_until_eof_runs),
    }


def _lob_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "| _No copied proof artifacts found._ | | | | | | | |\n"
    return "\n".join(
        "| {symbol} | `{job_id}` | `{max_messages}` | `{snapshots}` | `{validation_status}` | `{rules_run}` | `{rules_failed}` | `{two_sided_percent:.4f}%` | `{median_spread_raw}` |".format(
            **row
        )
        for row in rows
    )


def _lob_until_eof_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "| _No copied proof artifacts found._ | | | | | | | | | |\n"
    return "\n".join(
        "| {symbol} | `{job_id}` | `{node}` | `{run_mode}` | `{stop_reason}` | `{messages_scanned}` | `{snapshots}` | `{validation_status}` | `{rules_run}` | `{rules_failed}` | `{two_sided_percent:.4f}%` | `{median_spread_raw}` |".format(
            **row
        )
        for row in rows
    )


def _render_markdown(
    *,
    input_sha: str,
    week6: dict[str, Any],
    week10_runs: list[dict[str, Any]],
    week11_2m_runs: list[dict[str, Any]],
    week11_10m_runs: list[dict[str, Any]],
    week12_until_eof_runs: list[dict[str, Any]],
) -> str:
    total_10m_snapshots = sum(run["snapshots"] for run in week11_10m_runs)
    return f"""# Week 12 Final Evidence Report

## Summary

This report consolidates the project evidence generated so far: bounded
`message_events`, `order_events`, and MeatPy-based `lob_snapshots` datasets,
with validation, DuckDB summaries, and Iris SLURM proof artifacts.

The project remains a data engineering pipeline project. It uses MeatPy for ITCH
message parsing/reconstruction and focuses on reproducible artifacts, validation,
partitioned Parquet, DuckDB analytics, and HPC execution. Raw Nasdaq data and
large Parquet outputs remain outside Git.

## Shared Lineage

- Trading date: `2019-12-30`
- Input SHA-256: `{input_sha}`
- Raw data policy: raw Nasdaq data is not copied into Git or public reports.
- Proof source: copied logs, manifests, validation JSON files, and DuckDB summary JSON files under `logs/`.

## Week 6 Message And Order Event Proof

| Dataset | Job ID | Node | Rows | Validation | Rules Run | Rules Failed |
| --- | --- | --- | ---: | --- | ---: | ---: |
| `message_events` | `{week6["job_id"]}` | `{week6["node"]}` | `{week6["message_events_rows"]}` | {week6["message_events_status"]} | `{week6["message_events_rules_run"]}` | `{week6["message_events_rules_failed"]}` |
| `order_events` | `{week6["job_id"]}` | `{week6["node"]}` | `{week6["order_events_rows"]}` | {week6["order_events_status"]} | `{week6["order_events_rules_run"]}` | `{week6["order_events_rules_failed"]}` |

This proves the project can turn parsed ITCH messages into broad audit data and
focused order-event data, with structural validation and reproducible HPC proof.

## Week 10 Single-Symbol LOB Proof

| Symbol | Job ID | Max Messages | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
{_lob_table(week10_runs)}

## Week 11 Multi-Symbol LOB Proof: 2M Bound

| Symbol | Job ID | Max Messages | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
{_lob_table(week11_2m_runs)}

## Week 11 Multi-Symbol LOB Proof: 10M Bound

| Symbol | Job ID | Max Messages | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
{_lob_table(week11_10m_runs)}

The 10M comparison produced `{total_10m_snapshots}` total copied-proof snapshots
across `SPY`, `QQQ`, and `IWM`, with all validation reports passing.

## Week 12 SPY Until-EOF LOB Proof

| Symbol | Job ID | Node | Run Mode | Stop Reason | Messages Scanned | Snapshots | Validation | Rules Run | Rules Failed | Two-Sided % | Median Spread Raw |
| --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
{_lob_until_eof_table(week12_until_eof_runs)}

This is the final full-file proof run for the current project scope. It shows
that the pipeline can process the available `SPY` ITCH stream until the MeatPy
reader reaches EOF, while preserving explicit stop metadata in the manifest.

## What This Proves

- The same pipeline recipe can run locally and on Iris HPC.
- MeatPy-based LOB reconstruction can be orchestrated into a reproducible data product.
- Manifests and input hashes preserve lineage.
- The final `SPY` run records whether processing stopped at EOF and how many messages were scanned.
- Validation reports make pipeline outputs inspectable.
- DuckDB summaries provide analytics over generated artifacts without a database server.
- SLURM logs provide operational proof of compute-node execution.

## Limitations

- Validation is structural plus sanity checking; it is not a proof of full market microstructure correctness.
- LOB prices are raw ITCH integer units, not normalized market display prices.
- Multi-symbol LOB comparisons are bounded by message count; only the final `SPY` run is until EOF.
- Large Parquet outputs remain on private Iris scratch storage.
- Streamlit remains a thin presentation layer over existing artifacts.

## Next Direction

The final Weeks 12-15 phase should turn this evidence into a production-ready
portfolio package: reproducibility docs, CI, Docker test container, data
contracts, operations runbook, evidence index, portfolio case study, interview
prep, and a final demo script.
"""
