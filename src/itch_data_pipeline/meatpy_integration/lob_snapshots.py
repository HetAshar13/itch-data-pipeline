from __future__ import annotations

import datetime as dt
from itertools import islice
from pathlib import Path
from typing import Any

from meatpy.itch50 import (
    AddOrderMessage,
    AddOrderMPIDMessage,
    ITCH50MarketProcessor,
    ITCH50MessageReader,
    OrderCancelMessage,
    OrderDeleteMessage,
    OrderExecutedMessage,
    OrderExecutedPriceMessage,
    OrderReplaceMessage,
)


LOB_SNAPSHOT_DEPTH = 5

LOB_SNAPSHOT_COLUMNS = [
    "snapshot_number",
    "sequence_number",
    "timestamp_ns",
    "symbol",
    "source_message_type",
    "source_message_class",
    *[f"bid_price_{level}_raw" for level in range(1, LOB_SNAPSHOT_DEPTH + 1)],
    *[f"bid_size_{level}" for level in range(1, LOB_SNAPSHOT_DEPTH + 1)],
    *[f"ask_price_{level}_raw" for level in range(1, LOB_SNAPSHOT_DEPTH + 1)],
    *[f"ask_size_{level}" for level in range(1, LOB_SNAPSHOT_DEPTH + 1)],
    "spread_1_raw",
    "mid_price_1_raw",
    "level1_imbalance",
]

LOB_CHANGING_MESSAGE_TYPES = (
    AddOrderMessage,
    AddOrderMPIDMessage,
    OrderCancelMessage,
    OrderDeleteMessage,
    OrderExecutedMessage,
    OrderExecutedPriceMessage,
    OrderReplaceMessage,
)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("ascii", errors="replace").strip() or None
    text = str(value).strip()
    return text if text else None


def _level_price(level: Any) -> int:
    return int(level.price)


def _level_size(level: Any) -> int:
    return int(level.volume)


def _level1_spread_raw(best_bid_price: int | None, best_ask_price: int | None) -> int | None:
    if best_bid_price is None or best_ask_price is None:
        return None
    return best_ask_price - best_bid_price


def _level1_mid_raw(best_bid_price: int | None, best_ask_price: int | None) -> float | None:
    if best_bid_price is None or best_ask_price is None:
        return None
    return (best_bid_price + best_ask_price) / 2


def _level1_imbalance(best_bid_size: int | None, best_ask_size: int | None) -> float | None:
    if best_bid_size is None or best_ask_size is None:
        return None
    total_size = best_bid_size + best_ask_size
    if total_size == 0:
        return None
    return (best_bid_size - best_ask_size) / total_size


def lob_to_snapshot_row(
    lob: Any,
    *,
    snapshot_number: int,
    sequence_number: int,
    timestamp_ns: int,
    symbol: str,
    source_message: Any,
    depth: int = LOB_SNAPSHOT_DEPTH,
) -> dict[str, Any]:
    if depth != LOB_SNAPSHOT_DEPTH:
        raise ValueError(f"lob_snapshots v1 requires depth={LOB_SNAPSHOT_DEPTH}")
    if lob is None:
        raise ValueError("lob is required")

    bid_levels = lob.get_bid_levels(depth)
    ask_levels = lob.get_ask_levels(depth)

    row: dict[str, Any] = {
        "snapshot_number": int(snapshot_number),
        "sequence_number": int(sequence_number),
        "timestamp_ns": int(timestamp_ns),
        "symbol": symbol.upper(),
        "source_message_type": _clean_text(getattr(source_message, "type", None)),
        "source_message_class": type(source_message).__name__,
    }

    for level in range(1, depth + 1):
        bid = bid_levels[level - 1] if level <= len(bid_levels) else None
        ask = ask_levels[level - 1] if level <= len(ask_levels) else None
        row[f"bid_price_{level}_raw"] = _level_price(bid) if bid is not None else None
        row[f"bid_size_{level}"] = _level_size(bid) if bid is not None else None
        row[f"ask_price_{level}_raw"] = _level_price(ask) if ask is not None else None
        row[f"ask_size_{level}"] = _level_size(ask) if ask is not None else None

    best_bid_price = row["bid_price_1_raw"]
    best_ask_price = row["ask_price_1_raw"]
    best_bid_size = row["bid_size_1"]
    best_ask_size = row["ask_size_1"]

    row["spread_1_raw"] = _level1_spread_raw(best_bid_price, best_ask_price)
    row["mid_price_1_raw"] = _level1_mid_raw(best_bid_price, best_ask_price)
    row["level1_imbalance"] = _level1_imbalance(best_bid_size, best_ask_size)

    return {column: row[column] for column in LOB_SNAPSHOT_COLUMNS}


def _instrument_bytes(symbol: str) -> bytes:
    return f"{symbol.upper():<8}".encode("ascii")


def _active_order_refs(processor: ITCH50MarketProcessor) -> set[int]:
    return set(getattr(processor, "_order_refs", set()))


def _message_changes_target_lob(message: Any, symbol_bytes: bytes, active_order_refs: set[int]) -> bool:
    if isinstance(message, (AddOrderMessage, AddOrderMPIDMessage)):
        return getattr(message, "stock", None) == symbol_bytes
    if isinstance(
        message,
        (
            OrderCancelMessage,
            OrderDeleteMessage,
            OrderExecutedMessage,
            OrderExecutedPriceMessage,
        ),
    ):
        return getattr(message, "order_ref", None) in active_order_refs
    if isinstance(message, OrderReplaceMessage):
        return getattr(message, "original_ref", None) in active_order_refs
    return False


def extract_lob_snapshot_rows(
    input_path: str | Path,
    *,
    date: str,
    symbol: str,
    max_messages: int,
) -> list[dict[str, Any]]:
    result = extract_lob_snapshot_rows_with_metadata(
        input_path,
        date=date,
        symbol=symbol,
        max_messages=max_messages,
    )
    return result["rows"]


def extract_lob_snapshot_rows_with_metadata(
    input_path: str | Path,
    *,
    date: str,
    symbol: str,
    max_messages: int | None,
) -> dict[str, Any]:
    if max_messages is not None and max_messages < 1:
        raise ValueError("max_messages must be at least 1")

    symbol = symbol.upper()
    symbol_bytes = _instrument_bytes(symbol)
    book_date = dt.datetime.fromisoformat(date)
    processor = ITCH50MarketProcessor(symbol, book_date)
    rows: list[dict[str, Any]] = []
    messages_scanned = 0

    with ITCH50MessageReader(Path(input_path)) as reader:
        messages = reader if max_messages is None else islice(reader, max_messages)
        for sequence_number, message in enumerate(messages, start=1):
            messages_scanned = sequence_number
            active_refs_before = _active_order_refs(processor)
            should_snapshot = _message_changes_target_lob(
                message,
                symbol_bytes,
                active_refs_before,
            )

            processor.process_message(message)

            if should_snapshot and processor.current_lob is not None:
                rows.append(
                    lob_to_snapshot_row(
                        processor.current_lob,
                        snapshot_number=len(rows) + 1,
                        sequence_number=sequence_number,
                        timestamp_ns=int(getattr(message, "timestamp")),
                        symbol=symbol,
                        source_message=message,
                    )
                )

    stop_reason = "eof"
    if max_messages is not None and messages_scanned == max_messages:
        stop_reason = "max_messages_reached"

    return {
        "rows": rows,
        "messages_scanned": messages_scanned,
        "stop_reason": stop_reason,
    }
