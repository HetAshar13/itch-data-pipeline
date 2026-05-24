import json
from pathlib import Path

import pandas as pd
import pytest

from itch_data_pipeline import cli
from itch_data_pipeline.cli import extract_itch50_sample
from itch_data_pipeline.meatpy_integration import extract
from itch_data_pipeline.runner import extract_itch50_sample as extract_runner


class FakeSystemEventMessage:
    type = b"S"
    stock_locate = 0
    tracking_number = 7
    timestamp = 123456789
    description = "System Event Message"


class FakeStockMessage:
    type = b"R"
    stock_locate = 12
    tracking_number = 8
    timestamp = 223456789
    stock = b"AAPL    "
    description = "Stock Directory Message"


class FakeReader:
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        return iter(
            [
                FakeSystemEventMessage(),
                FakeStockMessage(),
                FakeStockMessage(),
            ]
        )

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_message_to_event_row_extracts_stable_common_fields():
    row = extract.message_to_event_row(FakeStockMessage(), sequence_number=2)

    assert row == {
        "sequence_number": 2,
        "message_type": "R",
        "message_class": "FakeStockMessage",
        "stock_locate": 12,
        "tracking_number": 8,
        "timestamp_ns": 223456789,
        "stock": "AAPL",
        "description": "Stock Directory Message",
    }


def test_extract_message_event_rows_respects_max_messages(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(extract, "ITCH50MessageReader", FakeReader)

    rows = extract.extract_message_event_rows(tmp_path / "sample.itch50.gz", max_messages=2)

    assert len(rows) == 2
    assert [row["sequence_number"] for row in rows] == [1, 2]
    assert [row["message_type"] for row in rows] == ["S", "R"]


def test_extract_message_event_rows_rejects_non_positive_max(tmp_path: Path):
    with pytest.raises(ValueError, match="max_messages must be at least 1"):
        extract.extract_message_event_rows(tmp_path / "sample.itch50.gz", max_messages=0)


def test_run_extract_itch50_sample_writes_parquet_and_manifest(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    monkeypatch.setattr(
        extract_runner,
        "extract_message_event_rows",
        lambda input_file, max_messages: [
            extract.message_to_event_row(FakeSystemEventMessage(), 1),
            extract.message_to_event_row(FakeStockMessage(), 2),
        ],
    )
    monkeypatch.setattr(
        extract_runner,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = extract_runner.run_extract_itch50_sample(
        input_path,
        date="2019-12-30",
        output_root=output_root,
        max_messages=2,
    )

    parquet_path = Path(result["parquet_path"])
    manifest_path = Path(result["manifest_path"])
    frame = pd.read_parquet(parquet_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert parquet_path.exists()
    assert manifest_path.exists()
    assert result["rows_written"] == 2
    assert list(frame["message_type"]) == ["S", "R"]
    assert manifest["output_paths"] == [str(parquet_path)]
    assert manifest["row_counts"]["message_events"] == 2
    assert manifest["max_messages"] == 2
    assert manifest["validation_summary"]["status"] == "not_run"


def test_run_extract_itch50_sample_uses_message_events_partition(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    monkeypatch.setattr(
        extract_runner,
        "extract_message_event_rows",
        lambda input_file, max_messages: [extract.message_to_event_row(FakeSystemEventMessage(), 1)],
    )
    monkeypatch.setattr(
        extract_runner,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = extract_runner.run_extract_itch50_sample(
        input_path,
        date="2019-12-30",
        output_root=output_root,
        max_messages=1,
    )

    assert Path(result["parquet_path"]).parent == (
        output_root / "dataset=message_events" / "date=2019-12-30" / "symbol=ALL"
    )


def test_extract_itch50_sample_cli_prints_json_output_locations(capsys, monkeypatch):
    def fake_run_extract_itch50_sample(input_path, date, output_root="outputs/local", max_messages=100_000):
        return {
            "parquet_path": f"{output_root}/part-000.parquet",
            "manifest_path": f"{output_root}/manifest.json",
            "rows_written": max_messages,
        }

    monkeypatch.setattr(cli, "run_extract_itch50_sample", fake_run_extract_itch50_sample)

    extract_itch50_sample(
        "sample.itch50.gz",
        date="2019-12-30",
        output_root="outputs/test",
        max_messages=3,
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["parquet_path"] == "outputs/test/part-000.parquet"
    assert result["manifest_path"] == "outputs/test/manifest.json"
    assert result["rows_written"] == 3
