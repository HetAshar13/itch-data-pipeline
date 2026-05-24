import json
from pathlib import Path

from itch_data_pipeline import cli
from itch_data_pipeline.cli import write_week12_report
from itch_data_pipeline.reporting.week12_report import build_week12_final_report


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_lob_proof(proof_dir: Path, *, symbol: str, job_id: str, max_messages: int, snapshots: int) -> None:
    proof_dir.mkdir(parents=True, exist_ok=True)
    (proof_dir / f"itch_lob_snapshots_{job_id}.out").write_text(
        f"Job started on iris-111\nSLURM_JOB_ID={job_id}\nJob finished\n",
        encoding="utf-8",
    )
    write_json(
        proof_dir / f"lob_manifest_{symbol}_2019-12-30_{job_id}.json",
        {
            "input_sha256": "abc123",
            "max_messages": max_messages,
            "duration_seconds": 12.3,
            "row_counts": {"lob_snapshots": snapshots},
        },
    )
    write_json(
        proof_dir / f"lob_validation_{symbol}_2019-12-30_{job_id}.json",
        {
            "status": "passed",
            "rules_run": 8,
            "rules_failed": 0,
        },
    )
    write_json(
        proof_dir / f"lob_summary_{symbol}_2019-12-30_{job_id}.json",
        {
            "snapshot_count": snapshots,
            "two_sided_snapshot_count": snapshots - 1,
            "two_sided_snapshot_percent": 99.5,
            "median_spread_1_raw": 300.0,
            "avg_spread_1_raw": 325.0,
            "avg_level1_imbalance": 0.01,
        },
    )


def write_lob_until_eof_proof(proof_dir: Path, *, symbol: str, job_id: str, messages_scanned: int, snapshots: int) -> None:
    proof_dir.mkdir(parents=True, exist_ok=True)
    (proof_dir / f"itch_lob_until_eof_{job_id}.out").write_text(
        f"Job started on iris-111\nSLURM_JOB_ID={job_id}\nRUN_MODE=until_eof\nJob finished\n",
        encoding="utf-8",
    )
    write_json(
        proof_dir / f"lob_manifest_{symbol}_2019-12-30_until_eof_{job_id}.json",
        {
            "input_sha256": "abc123",
            "run_mode": "until_eof",
            "stop_reason": "eof",
            "messages_scanned": messages_scanned,
            "duration_seconds": 123.4,
            "row_counts": {"lob_snapshots": snapshots},
        },
    )
    write_json(
        proof_dir / f"lob_validation_{symbol}_2019-12-30_until_eof_{job_id}.json",
        {
            "status": "passed",
            "rules_run": 8,
            "rules_failed": 0,
        },
    )
    write_json(
        proof_dir / f"lob_summary_{symbol}_2019-12-30_until_eof_{job_id}.json",
        {
            "snapshot_count": snapshots,
            "two_sided_snapshot_count": snapshots - 1,
            "two_sided_snapshot_percent": 99.9,
            "median_spread_1_raw": 200.0,
            "avg_spread_1_raw": 270.0,
            "avg_level1_imbalance": -0.03,
        },
    )


def write_week12_proof_root(proof_root: Path) -> None:
    proof_root.mkdir(parents=True, exist_ok=True)
    (proof_root / "hpc_week6_5386100.out").write_text(
        "Job started on iris-111\nSLURM_JOB_ID=5386100\nJob finished\n",
        encoding="utf-8",
    )
    write_json(
        proof_root / "hpc_message_events_validation_5386100.json",
        {
            "row_count": 100,
            "status": "passed",
            "rules_run": 4,
            "rules_failed": 0,
        },
    )
    write_json(
        proof_root / "hpc_order_events_validation_5386100.json",
        {
            "row_count": 75,
            "status": "passed",
            "rules_run": 7,
            "rules_failed": 0,
        },
    )
    write_lob_proof(proof_root / "week10_lob_5404108", symbol="SPY", job_id="5404108", max_messages=2_000_000, snapshots=10)
    write_lob_proof(proof_root / "week11_lob_2m", symbol="QQQ", job_id="5404160", max_messages=2_000_000, snapshots=20)
    write_lob_proof(proof_root / "week11_lob_10m", symbol="SPY", job_id="5404209", max_messages=10_000_000, snapshots=30)
    write_lob_until_eof_proof(
        proof_root / "week12_lob_until_eof_5406828",
        symbol="SPY",
        job_id="5406828",
        messages_scanned=29156757,
        snapshots=40,
    )


def test_build_week12_final_report_reads_copied_proof_artifacts(tmp_path: Path):
    proof_root = tmp_path / "logs"
    write_week12_proof_root(proof_root)
    report_path = tmp_path / "reports" / "week12_final_report.md"

    result = build_week12_final_report(proof_root=proof_root, report_path=report_path)
    content = report_path.read_text(encoding="utf-8")

    assert result["report_path"] == str(report_path)
    assert result["week6_message_events_rows"] == 100
    assert result["week6_order_events_rows"] == 75
    assert result["week10_lob_runs"] == 1
    assert result["week11_2m_lob_runs"] == 1
    assert result["week11_10m_lob_runs"] == 1
    assert result["week11_10m_total_snapshots"] == 30
    assert result["week12_until_eof_lob_runs"] == 1
    assert result["week12_until_eof_messages_scanned"] == 29156757
    assert result["week12_until_eof_snapshots"] == 40
    assert "Week 12 Final Evidence Report" in content
    assert "| `message_events` | `5386100` | `iris-111` | `100` | passed | `4` | `0` |" in content
    assert "| SPY | `5404209` | `10000000` | `30` | `passed` | `8` | `0` | `99.5000%` | `300.0` |" in content
    assert "Week 12 SPY Until-EOF LOB Proof" in content
    assert "| SPY | `5406828` | `iris-111` | `until_eof` | `eof` | `29156757` | `40` | `passed` | `8` | `0` | `99.9000%` | `200.0` |" in content
    assert "Raw Nasdaq data" in content
    assert "large Parquet outputs remain outside Git" in content


def test_write_week12_report_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "build_week12_final_report",
        lambda proof_root="logs", report_path="reports/week12_final_report.md": {
            "report_path": report_path,
            "week6_message_events_rows": 100,
            "week6_order_events_rows": 75,
            "week10_lob_runs": 1,
            "week11_2m_lob_runs": 3,
            "week11_10m_lob_runs": 3,
            "week11_10m_total_snapshots": 535626,
            "week12_until_eof_lob_runs": 1,
            "week12_until_eof_messages_scanned": 29156757,
            "week12_until_eof_snapshots": 614578,
        },
    )

    write_week12_report(proof_root="logs/test", report_path="reports/week12_test.md")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["report_path"] == "reports/week12_test.md"
    assert result["week11_10m_total_snapshots"] == 535626
    assert result["week12_until_eof_messages_scanned"] == 29156757
