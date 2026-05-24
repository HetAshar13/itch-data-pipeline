import json
from pathlib import Path

import pandas as pd

from itch_data_pipeline import cli
from itch_data_pipeline.cli import validate_order_events
from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.order_events import ORDER_EVENT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path
from itch_data_pipeline.validation.order_events import validate_order_events_partition


def valid_order_event_rows() -> list[dict]:
    return [
        {
            "sequence_number": 1,
            "event_type": "add",
            "message_type": "A",
            "message_class": "AddOrderMessage",
            "stock_locate": 1,
            "tracking_number": 0,
            "timestamp_ns": 100,
            "order_ref": 10,
            "original_ref": None,
            "new_ref": None,
            "side": "B",
            "shares": 100,
            "price": 123400,
            "canceled_shares": None,
            "match_number": None,
            "stock": "AAPL",
            "description": "Add Order Message",
        },
        {
            "sequence_number": 2,
            "event_type": "replace",
            "message_type": "U",
            "message_class": "OrderReplaceMessage",
            "stock_locate": 1,
            "tracking_number": 0,
            "timestamp_ns": 101,
            "order_ref": None,
            "original_ref": 10,
            "new_ref": 11,
            "side": None,
            "shares": 50,
            "price": 123500,
            "canceled_shares": None,
            "match_number": None,
            "stock": None,
            "description": "Order Replace Message",
        },
    ]


def write_order_events_partition(
    output_root: Path,
    rows: list[dict] | None = None,
    manifest_count: int | None = None,
    date: str = "2019-12-30",
) -> Path:
    rows = valid_order_event_rows() if rows is None else rows
    manifest_count = len(rows) if manifest_count is None else manifest_count
    out_dir = partition_path(output_root, "order_events", date, "ALL")
    out_dir.mkdir(parents=True)
    pd.DataFrame(rows, columns=ORDER_EVENT_COLUMNS).to_parquet(out_dir / "part-000.parquet", index=False)
    write_manifest({"row_counts": {"order_events": manifest_count}}, out_dir / "manifest.json")
    return out_dir


def test_validate_order_events_partition_writes_passing_report(tmp_path: Path):
    out_dir = write_order_events_partition(tmp_path)

    result = validate_order_events_partition(tmp_path, date="2019-12-30")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "passed"
    assert result["rules_failed"] == 0
    assert report["row_count"] == 2
    assert report["rules_run"] == 7


def test_validate_order_events_partition_reports_missing_parquet(tmp_path: Path):
    result = validate_order_events_partition(tmp_path, date="2019-12-30")
    report_path = (
        partition_path(tmp_path, "order_events", "2019-12-30", "ALL")
        / "validation_report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(finding["rule_name"] == "parquet_file_exists" for finding in report["findings"])


def test_validate_order_events_partition_reports_missing_order_refs(tmp_path: Path):
    rows = valid_order_event_rows()
    rows[0]["order_ref"] = None
    out_dir = write_order_events_partition(tmp_path, rows=rows)

    result = validate_order_events_partition(tmp_path, date="2019-12-30")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "order_refs_present" and finding["violations"] == 1
        for finding in report["findings"]
    )


def test_validate_order_events_partition_reports_manifest_mismatch(tmp_path: Path):
    out_dir = write_order_events_partition(tmp_path, manifest_count=99)

    result = validate_order_events_partition(tmp_path, date="2019-12-30")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "manifest_row_count_matches_parquet"
        and finding["status"] == "failed"
        for finding in report["findings"]
    )


def test_validate_order_events_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "validate_order_events_partition",
        lambda output_root, date, symbol="ALL": {
            "validation_report_path": "outputs/report.json",
            "status": "passed",
            "rules_run": 7,
            "rules_failed": 0,
        },
    )

    validate_order_events("outputs/local", date="2019-12-30")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["status"] == "passed"
    assert result["rules_run"] == 7
    assert result["rules_failed"] == 0
