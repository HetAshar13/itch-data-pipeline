from __future__ import annotations

from collections import Counter
from itertools import islice
from pathlib import Path
from typing import Any

from meatpy.itch50 import ITCH50MessageReader


def _message_type_name(message: Any) -> str:
    message_type = getattr(message, "type", "unknown")
    if isinstance(message_type, bytes):
        return message_type.decode("ascii", errors="replace")
    return str(message_type)


def summarize_itch50_messages(input_path: str | Path, limit: int = 10) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    path = Path(input_path)
    counts: Counter[str] = Counter()
    classes: Counter[str] = Counter()
    messages_read = 0

    with ITCH50MessageReader(path) as reader:
        for message in islice(reader, limit):
            counts[_message_type_name(message)] += 1
            classes[type(message).__name__] += 1
            messages_read += 1

    return {
        "input_file": str(path),
        "limit": limit,
        "messages_read": messages_read,
        "message_type_counts": dict(sorted(counts.items())),
        "message_class_counts": dict(sorted(classes.items())),
    }
