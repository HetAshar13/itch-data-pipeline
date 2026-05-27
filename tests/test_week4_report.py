import json
from pathlib import Path

from itch_data_pipeline import cli
from itch_data_pipeline.cli import write_week4_report
from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.reporting import week4_report
from itch_data_pipeline.utils.paths import partition_path


def write_report_inputs(output_root: Path, date: str = "2019-12-30") -> Path:
    out_dir = partition_path(output_root, "message_events", date, "ALL")
    out_dir.mkdir(parents=True)
    parquet_path = out_dir / "part-000.parquet"
    parquet_path.write_text("placeholder", encoding="utf-8")
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "max_messages": 100,
            "row_counts": {"message_events": 100},
            "status": "success",
        },
        out_dir / "manifest.json",
    )
    (out_dir / "validation_report.json").write_text(
        json.dumps({"status": "passed"}),
        encoding="utf-8",
    )
    return out_dir


def test_build_week4_showcase_report_writes_markdown(monkeypatch, tmp_path: Path):
    write_report_inputs(tmp_path)
    report_path = tmp_path / "reports" / "week4_showcase.md"
    monkeypatch.setattr(
        week4_report,
        "message_type_counts",
        lambda output_root, date, symbol="ALL", limit=10: [
            {
                "message_type": "A",
                "message_class": "AddOrderMessage",
                "row_count": 60,
            }
        ],
    )

    result = week4_report.build_week4_showcase_report(
        output_root=tmp_path,
        date="2019-12-30",
        report_path=report_path,
    )
    content = report_path.read_text(encoding="utf-8")

    assert result["report_path"] == str(report_path)
    assert result["row_count"] == 100
    assert result["validation_status"] == "passed"
    assert "Message Event Showcase Report" in content
    assert "| A | AddOrderMessage | 60 |" in content
    assert "What This Does Not Prove Yet" in content
    assert "The Streamlit app exists as a thin presentation layer over these artifacts." in content
    assert "It does not make Streamlit responsible for pipeline execution." in content
    assert "It does not include a Streamlit app yet." not in content


def test_write_week4_report_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "build_week4_showcase_report",
        lambda output_root, date, symbol="ALL", report_path="reports/week4_showcase.md", top_n=10: {
            "report_path": report_path,
            "row_count": 100,
            "validation_status": "passed",
        },
    )

    write_week4_report("outputs/local", date="2019-12-30", report_path="reports/test.md")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["report_path"] == "reports/test.md"
    assert result["row_count"] == 100
    assert result["validation_status"] == "passed"
