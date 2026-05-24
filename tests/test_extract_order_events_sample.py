import json
from pathlib import Path

import pandas as pd
import pytest

from itch_data_pipeline import cli
from itch_data_pipeline.cli import extract_order_events_sample
from itch_data_pipeline.meatpy_integration import order_events
from itch_data_pipeline.runner import extract_order_events_sample as order_runner


class FakeSystemEventMessage:
    type = b"S"
    stock_locate = 0
    tracking_number = 7
    timestamp = 123456789
    description = "System Event Message"


class FakeAddOrderMessage:
    type = b"A"
    stock_locate = 12
    tracking_number = 8
    timestamp = 223456789
    order_ref = 1001
    bsindicator = b"B"
    shares = 200
    stock = b"AAPL    "
    price = 1500000
    description = "Add Order Message"


class FakeReplaceMessage:
    type = b"U"
    stock_locate = 12
    tracking_number = 9
    timestamp = 323456789
    original_ref = 1001
    new_ref = 1002
    shares = 100
    price = 1500500
    description = "Order Replace Message"


class FakeAddOrderMPIDMessage:
    type = b"F"
    stock_locate = 12
    tracking_number = 10
    timestamp = 423456789
    order_ref = 1003
    bsindicator = b"S"
    shares = 300
    stock = b"MSFT    "
    price = 2500000
    attribution = b"VIRT"
    description = "Add Order MPID Message"


FakeAddOrderMessage.__name__ = "AddOrderMessage"
FakeReplaceMessage.__name__ = "OrderReplaceMessage"
FakeAddOrderMPIDMessage.__name__ = "AddOrderMPIDMessage"


class FakeReader:
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        return iter(
            [
                FakeSystemEventMessage(),
                FakeAddOrderMessage(),
                FakeReplaceMessage(),
            ]
        )

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_message_to_order_event_row_extracts_order_fields():
    row = order_events.message_to_order_event_row(FakeAddOrderMessage(), sequence_number=2)

    assert row == {
        "sequence_number": 2,
        "event_type": "add",
        "message_type": "A",
        "message_class": "AddOrderMessage",
        "stock_locate": 12,
        "tracking_number": 8,
        "timestamp_ns": 223456789,
        "order_ref": 1001,
        "original_ref": None,
        "new_ref": None,
        "side": "B",
        "shares": 200,
        "price": 1500000,
        "canceled_shares": None,
        "match_number": None,
        "stock": "AAPL",
        "description": "Add Order Message",
    }


def test_message_to_order_event_row_treats_mpid_add_as_add_event():
    row = order_events.message_to_order_event_row(FakeAddOrderMPIDMessage(), sequence_number=4)

    assert row["event_type"] == "add"
    assert row["message_type"] == "F"
    assert row["message_class"] == "AddOrderMPIDMessage"
    assert row["order_ref"] == 1003
    assert row["stock"] == "MSFT"


def test_extract_order_event_rows_filters_non_order_messages(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(order_events, "ITCH50MessageReader", FakeReader)

    rows = order_events.extract_order_event_rows(tmp_path / "sample.itch50.gz", max_messages=3)

    assert len(rows) == 2
    assert [row["sequence_number"] for row in rows] == [2, 3]
    assert [row["event_type"] for row in rows] == ["add", "replace"]


def test_extract_order_event_rows_rejects_non_positive_max(tmp_path: Path):
    with pytest.raises(ValueError, match="max_messages must be at least 1"):
        order_events.extract_order_event_rows(tmp_path / "sample.itch50.gz", max_messages=0)


def test_run_extract_order_events_sample_writes_parquet_and_manifest(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    monkeypatch.setattr(
        order_runner,
        "extract_order_event_rows",
        lambda input_file, max_messages: [
            order_events.message_to_order_event_row(FakeAddOrderMessage(), 2),
            order_events.message_to_order_event_row(FakeReplaceMessage(), 3),
        ],
    )
    monkeypatch.setattr(
        order_runner,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = order_runner.run_extract_order_events_sample(
        input_path,
        date="2019-12-30",
        output_root=output_root,
        max_messages=3,
    )

    parquet_path = Path(result["parquet_path"])
    manifest_path = Path(result["manifest_path"])
    frame = pd.read_parquet(parquet_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert parquet_path.parent == output_root / "dataset=order_events" / "date=2019-12-30" / "symbol=ALL"
    assert list(frame["event_type"]) == ["add", "replace"]
    assert result["rows_written"] == 2
    assert manifest["row_counts"]["order_events"] == 2
    assert manifest["max_messages"] == 3
    assert manifest["validation_summary"]["status"] == "not_run"


def test_extract_order_events_sample_cli_prints_json_output_locations(capsys, monkeypatch):
    def fake_run_extract_order_events_sample(input_path, date, output_root="outputs/local", max_messages=1_000_000):
        return {
            "parquet_path": f"{output_root}/part-000.parquet",
            "manifest_path": f"{output_root}/manifest.json",
            "rows_written": max_messages - 1,
        }

    monkeypatch.setattr(cli, "run_extract_order_events_sample", fake_run_extract_order_events_sample)

    extract_order_events_sample(
        "sample.itch50.gz",
        date="2019-12-30",
        output_root="outputs/test",
        max_messages=3,
    )

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["parquet_path"] == "outputs/test/part-000.parquet"
    assert result["manifest_path"] == "outputs/test/manifest.json"
    assert result["rows_written"] == 2
