import datetime as dt

from meatpy.itch50 import (
    AddOrderMessage,
    ITCH50MarketProcessor,
    OrderCancelMessage,
    OrderDeleteMessage,
    OrderReplaceMessage,
)


TRADE_DATE = dt.datetime(2019, 12, 30)


def add_order_message(
    *,
    order_ref: int = 1001,
    side: bytes = b"B",
    shares: int = 200,
    price: int = 1_500_000,
    stock: bytes = b"SPY     ",
    timestamp: int = 1_000_000,
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
    order_ref: int = 1001,
    canceled_shares: int = 50,
    timestamp: int = 2_000_000,
) -> OrderCancelMessage:
    message = OrderCancelMessage()
    message.timestamp = timestamp
    message.order_ref = order_ref
    message.canceled_shares = canceled_shares
    return message


def replace_message(
    *,
    original_ref: int = 1001,
    new_ref: int = 1002,
    shares: int = 100,
    price: int = 1_500_100,
    timestamp: int = 3_000_000,
) -> OrderReplaceMessage:
    message = OrderReplaceMessage()
    message.timestamp = timestamp
    message.original_ref = original_ref
    message.new_ref = new_ref
    message.shares = shares
    message.price = price
    return message


def delete_message(
    *,
    order_ref: int = 1001,
    timestamp: int = 4_000_000,
) -> OrderDeleteMessage:
    message = OrderDeleteMessage()
    message.timestamp = timestamp
    message.order_ref = order_ref
    return message


def test_meatpy_add_order_creates_bid_level_for_target_symbol():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)

    processor.process_message(add_order_message())

    bid_levels = processor.current_lob.get_bid_levels()
    ask_levels = processor.current_lob.get_ask_levels()

    assert len(bid_levels) == 1
    assert bid_levels[0].price == 1_500_000
    assert bid_levels[0].volume == 200
    assert bid_levels[0].queue[0].order_id == 1001
    assert ask_levels == []


def test_meatpy_ignores_add_order_for_other_symbol():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)

    processor.process_message(add_order_message(stock=b"QQQ     "))

    assert processor.current_lob is None


def test_meatpy_cancel_order_reduces_existing_bid_volume():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)

    processor.process_message(add_order_message())
    processor.process_message(cancel_message())

    bid_levels = processor.current_lob.get_bid_levels()

    assert len(bid_levels) == 1
    assert bid_levels[0].price == 1_500_000
    assert bid_levels[0].volume == 150
    assert bid_levels[0].queue[0].order_id == 1001
    assert bid_levels[0].queue[0].volume == 150


def test_meatpy_replace_order_updates_ref_price_and_volume():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)

    processor.process_message(add_order_message())
    processor.process_message(replace_message())

    bid_levels = processor.current_lob.get_bid_levels()

    assert len(bid_levels) == 1
    assert bid_levels[0].price == 1_500_100
    assert bid_levels[0].volume == 100
    assert bid_levels[0].queue[0].order_id == 1002
    assert bid_levels[0].queue[0].volume == 100


def test_meatpy_delete_order_removes_bid_level():
    processor = ITCH50MarketProcessor("SPY", TRADE_DATE)

    processor.process_message(add_order_message())
    processor.process_message(delete_message())

    assert processor.current_lob.get_bid_levels() == []
    assert processor.current_lob.get_ask_levels() == []

