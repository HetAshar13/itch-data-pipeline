import json
from pathlib import Path

from itch_data_pipeline import cli
from itch_data_pipeline.cli import write_week6_report
from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.reporting import week6_report
from itch_data_pipeline.utils.paths import partition_path


def write_week6_report_inputs(output_root: Path, date: str = "2019-12-30") -> None:
    message_dir = partition_path(output_root, "message_events", date, "ALL")
    order_dir = partition_path(output_root, "order_events", date, "ALL")
    message_dir.mkdir(parents=True)
    order_dir.mkdir(parents=True)
    (message_dir / "part-000.parquet").write_text("placeholder", encoding="utf-8")
    (order_dir / "part-000.parquet").write_text("placeholder", encoding="utf-8")
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "max_messages": 100,
            "row_counts": {"message_events": 100},
            "status": "success",
        },
        message_dir / "manifest.json",
    )
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "max_messages": 100,
            "row_counts": {"order_events": 42},
            "status": "success",
        },
        order_dir / "manifest.json",
    )
    (message_dir / "validation_report.json").write_text(
        json.dumps({"status": "passed"}),
        encoding="utf-8",
    )
    (order_dir / "validation_report.json").write_text(
        json.dumps({"status": "passed"}),
        encoding="utf-8",
    )


def test_build_week6_showcase_report_writes_markdown(monkeypatch, tmp_path: Path):
    write_week6_report_inputs(tmp_path)
    report_path = tmp_path / "reports" / "week6_showcase.md"
    monkeypatch.setattr(
        week6_report,
        "message_type_counts",
        lambda output_root, date, symbol="ALL", limit=10: [
            {"message_type": "A", "message_class": "AddOrderMessage", "row_count": 60}
        ],
    )
    monkeypatch.setattr(
        week6_report,
        "order_event_summary",
        lambda output_root, date, symbol="ALL", limit=10: {
            "event_counts": [{"event_type": "add", "row_count": 25}],
            "side_counts": [{"side": "B", "row_count": 10, "total_shares": 1000}],
            "top_stocks_by_adds": [{"stock": "AAPL", "add_count": 8, "total_add_shares": 800}],
            "activity_counts": {"add": 25},
        },
    )

    result = week6_report.build_week6_showcase_report(
        output_root=tmp_path,
        date="2019-12-30",
        report_path=report_path,
    )
    content = report_path.read_text(encoding="utf-8")

    assert result["report_path"] == str(report_path)
    assert result["message_events_row_count"] == 100
    assert result["order_events_row_count"] == 42
    assert result["order_events_validation_status"] == "passed"
    assert "Week 6 Showcase Report" in content
    assert "| A | AddOrderMessage | 60 |" in content
    assert "| add | 25 |" in content
    assert "It does not reconstruct the full order book." in content


def test_write_week6_report_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "build_week6_showcase_report",
        lambda output_root, date, symbol="ALL", report_path="reports/week6_showcase.md", top_n=10: {
            "report_path": report_path,
            "message_events_row_count": 100,
            "message_events_validation_status": "passed",
            "order_events_row_count": 42,
            "order_events_validation_status": "passed",
        },
    )

    write_week6_report("outputs/local", date="2019-12-30", report_path="reports/week6_test.md")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["report_path"] == "reports/week6_test.md"
    assert result["order_events_row_count"] == 42
    assert result["order_events_validation_status"] == "passed"
