import json
from pathlib import Path

import pandas as pd

from itch_data_pipeline import cli
from itch_data_pipeline.cli import validate_lob_snapshots
from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.lob_snapshots import LOB_SNAPSHOT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path
from itch_data_pipeline.validation.lob_snapshots import validate_lob_snapshots_partition


def valid_lob_snapshot_rows() -> list[dict]:
    row = {column: None for column in LOB_SNAPSHOT_COLUMNS}
    row.update(
        {
            "snapshot_number": 1,
            "sequence_number": 33112,
            "timestamp_ns": 25_204_435_833_095,
            "symbol": "SPY",
            "source_message_type": "A",
            "source_message_class": "AddOrderMessage",
            "bid_price_1_raw": 3_226_600,
            "bid_size_1": 500,
        }
    )
    return [row]


def write_lob_snapshots_partition(
    output_root: Path,
    rows: list[dict] | None = None,
    manifest_count: int | None = None,
    date: str = "2019-12-30",
    symbol: str = "SPY",
) -> Path:
    rows = valid_lob_snapshot_rows() if rows is None else rows
    manifest_count = len(rows) if manifest_count is None else manifest_count
    out_dir = partition_path(output_root, "lob_snapshots", date, symbol)
    out_dir.mkdir(parents=True)
    pd.DataFrame(rows, columns=LOB_SNAPSHOT_COLUMNS).to_parquet(out_dir / "part-000.parquet", index=False)
    write_manifest({"row_counts": {"lob_snapshots": manifest_count}}, out_dir / "manifest.json")
    return out_dir


def test_validate_lob_snapshots_partition_writes_passing_report(tmp_path: Path):
    out_dir = write_lob_snapshots_partition(tmp_path)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "passed"
    assert result["rules_run"] == 8
    assert result["rules_failed"] == 0
    assert report["dataset"] == "lob_snapshots"
    assert report["row_count"] == 1


def test_validate_lob_snapshots_partition_reports_missing_parquet(tmp_path: Path):
    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report_path = (
        partition_path(tmp_path, "lob_snapshots", "2019-12-30", "SPY")
        / "validation_report.json"
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(finding["rule_name"] == "parquet_file_exists" for finding in report["findings"])


def test_validate_lob_snapshots_partition_reports_manifest_mismatch(tmp_path: Path):
    out_dir = write_lob_snapshots_partition(tmp_path, manifest_count=99)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "manifest_row_count_matches_parquet"
        and finding["status"] == "failed"
        for finding in report["findings"]
    )


def test_validate_lob_snapshots_partition_reports_wrong_symbol(tmp_path: Path):
    rows = valid_lob_snapshot_rows()
    rows[0]["symbol"] = "QQQ"
    out_dir = write_lob_snapshots_partition(tmp_path, rows=rows)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "single_requested_symbol"
        and finding["status"] == "failed"
        for finding in report["findings"]
    )


def test_validate_lob_snapshots_partition_reports_non_increasing_sequence(tmp_path: Path):
    rows = valid_lob_snapshot_rows()
    second = rows[0].copy()
    second["snapshot_number"] = 2
    second["sequence_number"] = 1
    second["timestamp_ns"] = rows[0]["timestamp_ns"] + 1
    rows.append(second)
    out_dir = write_lob_snapshots_partition(tmp_path, rows=rows)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "sequence_numbers_increasing"
        and finding["status"] == "failed"
        for finding in report["findings"]
    )


def test_validate_lob_snapshots_partition_reports_decreasing_timestamps(tmp_path: Path):
    rows = valid_lob_snapshot_rows()
    second = rows[0].copy()
    second["snapshot_number"] = 2
    second["sequence_number"] = rows[0]["sequence_number"] + 1
    second["timestamp_ns"] = rows[0]["timestamp_ns"] - 1
    rows.append(second)
    out_dir = write_lob_snapshots_partition(tmp_path, rows=rows)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "timestamps_non_decreasing"
        and finding["status"] == "failed"
        for finding in report["findings"]
    )


def test_validate_lob_snapshots_partition_reports_crossed_top_of_book(tmp_path: Path):
    rows = valid_lob_snapshot_rows()
    rows[0]["bid_price_1_raw"] = 100
    rows[0]["ask_price_1_raw"] = 99
    out_dir = write_lob_snapshots_partition(tmp_path, rows=rows)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "failed"
    assert any(
        finding["rule_name"] == "top_of_book_not_crossed"
        and finding["violations"] == 1
        for finding in report["findings"]
    )


def test_validate_lob_snapshots_partition_allows_one_sided_book(tmp_path: Path):
    rows = valid_lob_snapshot_rows()
    rows[0]["bid_price_1_raw"] = 100
    rows[0]["ask_price_1_raw"] = None
    out_dir = write_lob_snapshots_partition(tmp_path, rows=rows)

    result = validate_lob_snapshots_partition(tmp_path, date="2019-12-30", symbol="SPY")
    report = json.loads((out_dir / "validation_report.json").read_text(encoding="utf-8"))

    assert result["status"] == "passed"
    assert any(
        finding["rule_name"] == "top_of_book_not_crossed"
        and finding["status"] == "passed"
        for finding in report["findings"]
    )


def test_validate_lob_snapshots_cli_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "validate_lob_snapshots_partition",
        lambda output_root, date, symbol: {
            "validation_report_path": "outputs/report.json",
            "status": "passed",
            "rules_run": 5,
            "rules_failed": 0,
        },
    )

    validate_lob_snapshots("outputs/local", date="2019-12-30", symbol="SPY")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["status"] == "passed"
    assert result["rules_run"] == 5
    assert result["rules_failed"] == 0
