import json
from pathlib import Path

import pandas as pd

from itch_data_pipeline.meatpy_integration.lob_snapshots import LOB_SNAPSHOT_COLUMNS
from itch_data_pipeline.runner import extract_lob_snapshots_sample as lob_runner


def sample_snapshot_row(sequence_number: int = 2) -> dict:
    row = {column: None for column in LOB_SNAPSHOT_COLUMNS}
    row.update(
        {
            "snapshot_number": 1,
            "sequence_number": sequence_number,
            "timestamp_ns": 1_000_000,
            "symbol": "SPY",
            "source_message_type": "A",
            "source_message_class": "AddOrderMessage",
            "bid_price_1_raw": 1_500_000,
            "bid_size_1": 200,
        }
    )
    return row


def test_run_extract_lob_snapshots_sample_writes_parquet_and_manifest(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    monkeypatch.setattr(
        lob_runner,
        "extract_lob_snapshot_rows_with_metadata",
        lambda input_file, date, symbol, max_messages: {
            "rows": [sample_snapshot_row()],
            "messages_scanned": max_messages,
            "stop_reason": "max_messages_reached",
        },
    )
    monkeypatch.setattr(
        lob_runner,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = lob_runner.run_extract_lob_snapshots_sample(
        input_path,
        date="2019-12-30",
        symbol="spy",
        output_root=output_root,
        max_messages=3,
    )

    parquet_path = Path(result["parquet_path"])
    manifest_path = Path(result["manifest_path"])
    frame = pd.read_parquet(parquet_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert parquet_path.parent == output_root / "dataset=lob_snapshots" / "date=2019-12-30" / "symbol=SPY"
    assert result["rows_written"] == 1
    assert list(frame.columns) == LOB_SNAPSHOT_COLUMNS
    assert frame.loc[0, "symbol"] == "SPY"
    assert frame.loc[0, "bid_price_1_raw"] == 1_500_000
    assert manifest["dataset"] == "lob_snapshots"
    assert manifest["symbol"] == "SPY"
    assert manifest["run_mode"] == "bounded"
    assert manifest["max_messages"] == 3
    assert manifest["until_eof"] is False
    assert manifest["messages_scanned"] == 3
    assert manifest["stop_reason"] == "max_messages_reached"
    assert manifest["snapshot_depth"] == 5
    assert manifest["row_counts"]["lob_snapshots"] == 1
    assert manifest["validation_summary"]["status"] == "not_run"
    assert manifest["exception_counts"] == {}
    assert result["messages_scanned"] == 3
    assert result["stop_reason"] == "max_messages_reached"


def test_run_extract_lob_snapshots_sample_until_eof_records_eof_metadata(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    monkeypatch.setattr(
        lob_runner,
        "extract_lob_snapshot_rows_with_metadata",
        lambda input_file, date, symbol, max_messages: {
            "rows": [sample_snapshot_row()],
            "messages_scanned": 4,
            "stop_reason": "eof",
        },
    )
    monkeypatch.setattr(
        lob_runner,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = lob_runner.run_extract_lob_snapshots_sample(
        input_path,
        date="2019-12-30",
        symbol="SPY",
        output_root=output_root,
        max_messages=3,
        until_eof=True,
    )

    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))

    assert manifest["run_mode"] == "until_eof"
    assert manifest["max_messages"] is None
    assert manifest["until_eof"] is True
    assert manifest["messages_scanned"] == 4
    assert manifest["stop_reason"] == "eof"
    assert result["messages_scanned"] == 4
    assert result["stop_reason"] == "eof"
