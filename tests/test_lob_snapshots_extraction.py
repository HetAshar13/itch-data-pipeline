from pathlib import Path

import pytest
from meatpy.itch50 import AddOrderMessage, OrderCancelMessage

from itch_data_pipeline.meatpy_integration import lob_snapshots


def add_order_message(
    *,
    order_ref: int,
    side: bytes,
    shares: int,
    price: int,
    timestamp: int,
    stock: bytes,
) -> AddOrderMessage:
    message = AddOrderMessage()
    message.timestamp = timestamp
    message.stock = stock
    message.order_ref = order_ref
    message.bsindicator = side
    message.shares = shares
    message.price = price
    return message


def cancel_message(
    *,
    order_ref: int,
    canceled_shares: int,
    timestamp: int,
) -> OrderCancelMessage:
    message = OrderCancelMessage()
    message.timestamp = timestamp
    message.order_ref = order_ref
    message.canceled_shares = canceled_shares
    return message


class FakeReader:
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        return iter(
            [
                add_order_message(
                    order_ref=9001,
                    side=b"B",
                    shares=999,
                    price=1_000_000,
                    timestamp=500_000,
                    stock=b"QQQ     ",
                ),
                add_order_message(
                    order_ref=1001,
                    side=b"B",
                    shares=200,
                    price=1_500_000,
                    timestamp=1_000_000,
                    stock=b"SPY     ",
                ),
                add_order_message(
                    order_ref=2001,
                    side=b"S",
                    shares=300,
                    price=1_500_200,
                    timestamp=2_000_000,
                    stock=b"SPY     ",
                ),
                cancel_message(
                    order_ref=1001,
                    canceled_shares=50,
                    timestamp=3_000_000,
                ),
            ]
        )

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_extract_lob_snapshot_rows_filters_symbol_and_snapshots_lob_changes(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(lob_snapshots, "ITCH50MessageReader", FakeReader)

    rows = lob_snapshots.extract_lob_snapshot_rows(
        tmp_path / "sample.itch50.gz",
        date="2019-12-30",
        symbol="SPY",
        max_messages=4,
    )

    assert [row["snapshot_number"] for row in rows] == [1, 2, 3]
    assert [row["sequence_number"] for row in rows] == [2, 3, 4]
    assert [row["source_message_class"] for row in rows] == [
        "AddOrderMessage",
        "AddOrderMessage",
        "OrderCancelMessage",
    ]
    assert rows[0]["bid_price_1_raw"] == 1_500_000
    assert rows[0]["ask_price_1_raw"] is None
    assert rows[1]["ask_price_1_raw"] == 1_500_200
    assert rows[1]["spread_1_raw"] == 200
    assert rows[2]["bid_size_1"] == 150
    assert rows[2]["level1_imbalance"] == pytest.approx(-1 / 3)


def test_extract_lob_snapshot_rows_respects_max_messages(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(lob_snapshots, "ITCH50MessageReader", FakeReader)

    rows = lob_snapshots.extract_lob_snapshot_rows(
        tmp_path / "sample.itch50.gz",
        date="2019-12-30",
        symbol="SPY",
        max_messages=2,
    )

    assert len(rows) == 1
    assert rows[0]["sequence_number"] == 2


def test_extract_lob_snapshot_rows_with_metadata_records_bounded_stop(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(lob_snapshots, "ITCH50MessageReader", FakeReader)

    result = lob_snapshots.extract_lob_snapshot_rows_with_metadata(
        tmp_path / "sample.itch50.gz",
        date="2019-12-30",
        symbol="SPY",
        max_messages=2,
    )

    assert result["messages_scanned"] == 2
    assert result["stop_reason"] == "max_messages_reached"
    assert len(result["rows"]) == 1


def test_extract_lob_snapshot_rows_with_metadata_can_scan_until_eof(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(lob_snapshots, "ITCH50MessageReader", FakeReader)

    result = lob_snapshots.extract_lob_snapshot_rows_with_metadata(
        tmp_path / "sample.itch50.gz",
        date="2019-12-30",
        symbol="SPY",
        max_messages=None,
    )

    assert result["messages_scanned"] == 4
    assert result["stop_reason"] == "eof"
    assert [row["sequence_number"] for row in result["rows"]] == [2, 3, 4]


def test_extract_lob_snapshot_rows_rejects_non_positive_max(tmp_path: Path):
    with pytest.raises(ValueError, match="max_messages must be at least 1"):
        lob_snapshots.extract_lob_snapshot_rows(
            tmp_path / "sample.itch50.gz",
            date="2019-12-30",
            symbol="SPY",
            max_messages=0,
        )


def test_extract_lob_snapshot_rows_with_metadata_rejects_non_positive_max(tmp_path: Path):
    with pytest.raises(ValueError, match="max_messages must be at least 1"):
        lob_snapshots.extract_lob_snapshot_rows_with_metadata(
            tmp_path / "sample.itch50.gz",
            date="2019-12-30",
            symbol="SPY",
            max_messages=0,
        )
