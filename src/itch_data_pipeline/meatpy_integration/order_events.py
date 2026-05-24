from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Any

from meatpy.itch50 import ITCH50MessageReader


ORDER_EVENT_COLUMNS = [
    "sequence_number",
    "event_type",
    "message_type",
    "message_class",
    "stock_locate",
    "tracking_number",
    "timestamp_ns",
    "order_ref",
    "original_ref",
    "new_ref",
    "side",
    "shares",
    "price",
    "canceled_shares",
    "match_number",
    "stock",
    "description",
]

ORDER_EVENT_TYPES_BY_CLASS = {
    "AddOrderMessage": "add",
    "AddOrderMPIDMessage": "add",
    "OrderDeleteMessage": "delete",
    "OrderExecutedMessage": "execute",
    "OrderCancelMessage": "cancel",
    "OrderReplaceMessage": "replace",
}


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("ascii", errors="replace").strip() or None
    text = str(value).strip()
    return text if text else None


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def is_order_event_message(message: Any) -> bool:
    return type(message).__name__ in ORDER_EVENT_TYPES_BY_CLASS


def message_to_order_event_row(message: Any, sequence_number: int) -> dict[str, Any]:
    message_class = type(message).__name__
    event_type = ORDER_EVENT_TYPES_BY_CLASS.get(message_class)
    return {
        "sequence_number": sequence_number,
        "event_type": event_type,
        "message_type": _clean_text(getattr(message, "type", None)),
        "message_class": message_class,
        "stock_locate": _optional_int(getattr(message, "stock_locate", None)),
        "tracking_number": _optional_int(getattr(message, "tracking_number", None)),
        "timestamp_ns": _optional_int(getattr(message, "timestamp", None)),
        "order_ref": _optional_int(getattr(message, "order_ref", None)),
        "original_ref": _optional_int(getattr(message, "original_ref", None)),
        "new_ref": _optional_int(getattr(message, "new_ref", None)),
        "side": _clean_text(getattr(message, "bsindicator", None)),
        "shares": _optional_int(getattr(message, "shares", None)),
        "price": _optional_int(getattr(message, "price", None)),
        "canceled_shares": _optional_int(getattr(message, "canceled_shares", None)),
        "match_number": _optional_int(getattr(message, "match", None)),
        "stock": _clean_text(getattr(message, "stock", None)),
        "description": _clean_text(getattr(message, "description", None)),
    }


def extract_order_event_rows(
    input_path: str | Path,
    max_messages: int,
) -> list[dict[str, Any]]:
    if max_messages < 1:
        raise ValueError("max_messages must be at least 1")

    rows = []
    with ITCH50MessageReader(Path(input_path)) as reader:
        for sequence_number, message in enumerate(islice(reader, max_messages), start=1):
            if is_order_event_message(message):
                rows.append(message_to_order_event_row(message, sequence_number))

    return rows
