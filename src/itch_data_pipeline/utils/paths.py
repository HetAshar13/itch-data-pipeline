from __future__ import annotations

from pathlib import Path


def partition_path(output_root: str | Path, dataset: str, date: str, symbol: str) -> Path:
    return Path(output_root) / f"dataset={dataset}" / f"date={date}" / f"symbol={symbol}"
