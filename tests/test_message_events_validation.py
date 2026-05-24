import json
from pathlib import Path

import pandas as pd

from itch_data_pipeline import cli
from itch_data_pipeline.cli import validate_message_events
from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.extract import MESSAGE_EVENT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path
from itch_data_pipeline.validation.message_events import validate_message_events_partition


def write_valid_message_events_partition(output_root: Path, date: str = "2019-12-30") -> Path:
    out_dir = partition_path(output_root, "message_events", date, "ALL")
    out_dir.mkdir(parents=True)
    parquet_path = out_dir / "part-000.parquet"
    manifest_path = out_dir / "manifest.json"

    pd.DataFrame(
        [
            {
                "sequence_number": 1,
                "message_type": "S",
                "message_class": "SystemEventMessage",
                "stock_locate": 0,
                "tracking_number": 0,
                "timestamp_ns": 123,
                "stock": None,
                "description": "System Event Message",
            }
        ],
        columns=MESSAGE_EVENT_COLUMNS,
    ).to_parquet(parquet_path, index=False)
    write_manifest({"row_counts": {"message_events": 1}}, manifest_path)
    return out_dir


def test_validate_message_events_partition_writes_passing_report(tmp_path: Path):
    out_dir = write_valid_message_events_partition(tmp_path)

    result = validate_message_events_partition(tmp_path, date="2019-12-30")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "passed"
    assert result["rules_failed"] == 0
    assert report["row_count"] == 1
    assert report["status"] == "passed"


def test_validate_message_events_partition_reports_missing_parquet(tmp_path: Path):
    result = validate_message_events_partition(tmp_path, date="2019-12-30")
    report_path = (
        partition_path(tmp_path, "message_events", "2019-12-30", "ALL")
        / "validation_report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert result["rules_failed"] > 0
    assert any(finding["rule_name"] == "parquet_file_exists" for finding in report["findings"])


def test_validate_message_events_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "validate_message_events_partition",
        lambda output_root, date, symbol="ALL": {
            "validation_report_path": "outputs/report.json",
            "status": "passed",
            "rules_run": 4,
            "rules_failed": 0,
        },
    )

    validate_message_events("outputs/local", date="2019-12-30")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["status"] == "passed"
    assert result["rules_run"] == 4
    assert result["rules_failed"] == 0
