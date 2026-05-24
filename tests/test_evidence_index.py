import json
from pathlib import Path

from itch_data_pipeline import cli
from itch_data_pipeline.cli import write_artifact_evidence_index
from itch_data_pipeline.reporting.evidence_index import build_artifact_evidence_index


def test_build_artifact_evidence_index_classifies_copied_proof_artifacts(tmp_path: Path):
    proof_root = tmp_path / "logs"
    run_dir = proof_root / "week11_lob_10m"
    run_dir.mkdir(parents=True)
    (run_dir / "itch_lob_snapshots_5404209.out").write_text("SLURM_JOB_ID=5404209\n", encoding="utf-8")
    (run_dir / "itch_lob_snapshots_5404209.err").write_text("pipeline log\n", encoding="utf-8")
    (run_dir / "lob_manifest_SPY_2019-12-30_5404209.json").write_text("{}", encoding="utf-8")
    (run_dir / "lob_validation_SPY_2019-12-30_5404209.json").write_text("{}", encoding="utf-8")
    (run_dir / "lob_summary_SPY_2019-12-30_5404209.json").write_text("{}", encoding="utf-8")
    (proof_root / "week11_lob_10m.tar.gz").write_bytes(b"small proof bundle")
    report_path = tmp_path / "reports" / "artifact_evidence_index.md"

    result = build_artifact_evidence_index(proof_root=proof_root, report_path=report_path)
    content = report_path.read_text(encoding="utf-8")

    assert result["artifact_count"] == 6
    assert result["counts_by_type"]["manifest"] == 1
    assert result["counts_by_type"]["validation_report"] == 1
    assert result["counts_by_type"]["duckdb_summary"] == 1
    assert result["counts_by_type"]["proof_bundle"] == 1
    assert "`week11_lob_10m/lob_manifest_SPY_2019-12-30_5404209.json`" in content
    assert "`5404209`" in content
    assert "Raw Nasdaq data and large Parquet outputs are intentionally excluded" in content


def test_write_artifact_evidence_index_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "build_artifact_evidence_index",
        lambda proof_root="logs", report_path="reports/artifact_evidence_index.md": {
            "report_path": report_path,
            "proof_root": proof_root,
            "artifact_count": 3,
            "counts_by_type": {"manifest": 1, "validation_report": 1, "duckdb_summary": 1},
        },
    )

    write_artifact_evidence_index(proof_root="logs/test", report_path="reports/test_index.md")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["report_path"] == "reports/test_index.md"
    assert result["proof_root"] == "logs/test"
    assert result["artifact_count"] == 3
