import json
from pathlib import Path

from itch_data_pipeline import cli
from itch_data_pipeline.cli import (
    extract_lob_snapshots_sample,
    healthcheck,
    peek_itch50,
    probe_meatpy_command,
    sample_peek_run,
    write_sample_manifest,
)


def test_healthcheck_prints_ok(capsys):
    healthcheck()

    captured = capsys.readouterr()

    assert "healthcheck: OK" in captured.out


def test_write_sample_manifest_creates_json_file(tmp_path: Path):
    output_path = tmp_path / "manifest.json"

    write_sample_manifest(str(output_path))

    manifest = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.exists()
    assert manifest["run_id"] == "sample_run_001"


def test_probe_meatpy_command_prints_json_status(capsys):
    probe_meatpy_command()

    captured = capsys.readouterr()
    status = json.loads(captured.out)

    assert "installed" in status
    assert "version" in status


def test_peek_itch50_prints_json_summary(capsys, monkeypatch):
    def fake_summarize(input_path: str, limit: int = 10):
        return {
            "input_file": input_path,
            "limit": limit,
            "messages_read": 2,
            "message_type_counts": {"R": 1, "S": 1},
            "message_class_counts": {
                "StockDirectoryMessage": 1,
                "SystemEventMessage": 1,
            },
        }

    monkeypatch.setattr(cli, "summarize_itch50_messages", fake_summarize)

    peek_itch50("sample.itch50.gz", limit=2)

    captured = capsys.readouterr()
    summary = json.loads(captured.out)

    assert summary["input_file"] == "sample.itch50.gz"
    assert summary["limit"] == 2
    assert summary["messages_read"] == 2


def test_sample_peek_run_prints_json_output_locations(capsys, monkeypatch):
    def fake_run_sample_peek(input_path: str, output_root: str = "outputs/local", limit: int = 10):
        return {
            "summary_path": f"{output_root}/summary.json",
            "manifest_path": f"{output_root}/manifest.json",
            "messages_read": limit,
        }

    monkeypatch.setattr(cli, "run_sample_peek", fake_run_sample_peek)

    sample_peek_run("sample.itch50.gz", output_root="outputs/test", limit=3)

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["summary_path"] == "outputs/test/summary.json"
    assert result["manifest_path"] == "outputs/test/manifest.json"
    assert result["messages_read"] == 3


def test_extract_lob_snapshots_sample_prints_json_output_locations(capsys, monkeypatch):
    def fake_run_extract_lob_snapshots_sample(
        input_path,
        date,
        symbol,
        output_root="outputs/local",
        max_messages=1_000_000,
        until_eof=False,
    ):
        return {
            "parquet_path": f"{output_root}/dataset=lob_snapshots/date={date}/symbol={symbol}/part-000.parquet",
            "manifest_path": f"{output_root}/dataset=lob_snapshots/date={date}/symbol={symbol}/manifest.json",
            "rows_written": max_messages - 1,
            "messages_scanned": max_messages,
            "stop_reason": "max_messages_reached",
        }

    monkeypatch.setattr(cli, "run_extract_lob_snapshots_sample", fake_run_extract_lob_snapshots_sample)

    extract_lob_snapshots_sample(
        "sample.itch50.gz",
        date="2019-12-30",
        symbol="SPY",
        output_root="outputs/test",
        max_messages=3,
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["parquet_path"] == "outputs/test/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/part-000.parquet"
    assert result["manifest_path"] == "outputs/test/dataset=lob_snapshots/date=2019-12-30/symbol=SPY/manifest.json"
    assert result["rows_written"] == 2
    assert result["messages_scanned"] == 3
    assert result["stop_reason"] == "max_messages_reached"


def test_extract_lob_snapshots_sample_can_request_until_eof(capsys, monkeypatch):
    def fake_run_extract_lob_snapshots_sample(
        input_path,
        date,
        symbol,
        output_root="outputs/local",
        max_messages=1_000_000,
        until_eof=False,
    ):
        return {
            "parquet_path": f"{output_root}/dataset=lob_snapshots/date={date}/symbol={symbol}/part-000.parquet",
            "manifest_path": f"{output_root}/dataset=lob_snapshots/date={date}/symbol={symbol}/manifest.json",
            "rows_written": 4,
            "messages_scanned": 10,
            "stop_reason": "eof" if until_eof else "max_messages_reached",
        }

    monkeypatch.setattr(cli, "run_extract_lob_snapshots_sample", fake_run_extract_lob_snapshots_sample)

    extract_lob_snapshots_sample(
        "sample.itch50.gz",
        date="2019-12-30",
        symbol="SPY",
        output_root="outputs/test",
        max_messages=3,
        until_eof=True,
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["rows_written"] == 4
    assert result["messages_scanned"] == 10
    assert result["stop_reason"] == "eof"
