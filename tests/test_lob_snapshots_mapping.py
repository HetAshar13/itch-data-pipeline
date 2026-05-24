import datetime as dt

import pytest
from meatpy.itch50 import AddOrderMessage, ITCH50MarketProcessor

from itch_data_pipeline.meatpy_integration.lob_snapshots import (
    LOB_SNAPSHOT_COLUMNS,
    lob_to_snapshot_row,
)


TRADE_DATE = dt.datetime(2019, 12, 30)


def add_order_message(
    *,
    order_ref: int,
    side: bytes,
    shares: int,
    price: int,
    timestamp: int,
    stock: bytes = b"SPY     ",
) -> AddOrderMessage:
    message = AddOrderMessage()
    message.timestamp = timestamp
    message.stock = stock
    message.order_ref = order_ref
    message.bsindicator = side
    message.shares = shares
    message.price = price
    return message


def test_lob_to_snapshot_row_maps_top_five_levels_and_metrics():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)
    source_message = add_order_message(
        order_ref=2001,
        side=b"S",
        shares=300,
        price=1_500_200,
        timestamp=3_000_000,
    )

    processor.process_message(
        add_order_message(order_ref=1001, side=b"B", shares=200, price=1_500_000, timestamp=1_000_000)
    )
    processor.process_message(
        add_order_message(order_ref=1002, side=b"B", shares=100, price=1_499_900, timestamp=2_000_000)
    )
    processor.process_message(source_message)

    row = lob_to_snapshot_row(
        processor.current_lob,
        snapshot_number=1,
        sequence_number=3,
        timestamp_ns=3_000_000,
        symbol="spy",
        source_message=source_message,
    )

    assert list(row) == LOB_SNAPSHOT_COLUMNS
    assert row["snapshot_number"] == 1
    assert row["sequence_number"] == 3
    assert row["timestamp_ns"] == 3_000_000
    assert row["symbol"] == "SPY"
    assert row["source_message_type"] == "A"
    assert row["source_message_class"] == "AddOrderMessage"
    assert row["bid_price_1_raw"] == 1_500_000
    assert row["bid_size_1"] == 200
    assert row["bid_price_2_raw"] == 1_499_900
    assert row["bid_size_2"] == 100
    assert row["ask_price_1_raw"] == 1_500_200
    assert row["ask_size_1"] == 300
    assert row["spread_1_raw"] == 200
    assert row["mid_price_1_raw"] == 1_500_100.0
    assert row["level1_imbalance"] == pytest.approx(-0.2)
    assert row["ask_price_2_raw"] is None
    assert row["ask_size_2"] is None


def test_lob_to_snapshot_row_keeps_metrics_empty_when_one_side_missing():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)
    source_message = add_order_message(
        order_ref=1001,
        side=b"B",
        shares=200,
        price=1_500_000,
        timestamp=1_000_000,
    )
    processor.process_message(source_message)

    row = lob_to_snapshot_row(
        processor.current_lob,
        snapshot_number=1,
        sequence_number=1,
        timestamp_ns=1_000_000,
        symbol="SPY",
        source_message=source_message,
    )

    assert row["bid_price_1_raw"] == 1_500_000
    assert row["ask_price_1_raw"] is None
    assert row["spread_1_raw"] is None
    assert row["mid_price_1_raw"] is None
    assert row["level1_imbalance"] is None


def test_lob_to_snapshot_row_rejects_non_v1_depth():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)
    source_message = add_order_message(
        order_ref=1001,
        side=b"B",
        shares=200,
        price=1_500_000,
        timestamp=1_000_000,
    )
    processor.process_message(source_message)

    with pytest.raises(ValueError, match="depth=5"):
        lob_to_snapshot_row(
            processor.current_lob,
            snapshot_number=1,
            sequence_number=1,
            timestamp_ns=1_000_000,
            symbol="SPY",
            source_message=source_message,
            depth=10,
        )

