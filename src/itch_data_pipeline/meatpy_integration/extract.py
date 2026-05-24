from __future__ import annotations

from itertools import islice
from pathlib import Path
from typing import Any

from meatpy.itch50 import ITCH50MessageReader


MESSAGE_EVENT_COLUMNS = [
    "sequence_number",
    "message_type",
    "message_class",
    "stock_locate",
    "tracking_number",
    "timestamp_ns",
    "stock",
    "description",
]


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("ascii", errors="replace").strip()
    text = str(value).strip()
    return text if text else None


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def message_to_event_row(message: Any, sequence_number: int) -> dict[str, Any]:
    return {
        "sequence_number": sequence_number,
        "message_type": _clean_text(getattr(message, "type", None)),
        "message_class": type(message).__name__,
        "stock_locate": _optional_int(getattr(message, "stock_locate", None)),
        "tracking_number": _optional_int(getattr(message, "tracking_number", None)),
        "timestamp_ns": _optional_int(getattr(message, "timestamp", None)),
        "stock": _clean_text(getattr(message, "stock", None)),
        "description": _clean_text(getattr(message, "description", None)),
    }


def extract_message_event_rows(
    input_path: str | Path,
    max_messages: int,
) -> list[dict[str, Any]]:
    if max_messages < 1:
        raise ValueError("max_messages must be at least 1")

    path = Path(input_path)
    rows = []

    with ITCH50MessageReader(path) as reader:
        for sequence_number, message in enumerate(islice(reader, max_messages), start=1):
            rows.append(message_to_event_row(message, sequence_number))

    return rows
