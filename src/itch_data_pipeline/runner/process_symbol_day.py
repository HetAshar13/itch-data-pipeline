from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SymbolDayJob:
    date: str
    symbol: str
    input_file: Path
    output_root: Path
    schema_version: str = "1.0"


def process_symbol_day(job: SymbolDayJob) -> None:
    """Future MeatPy-based processor for one symbol/day.

    TODO Week 2:
    - verify MeatPy can process a sample file
    - call MeatPy parser/processor/recorders
    - write structured outputs
    - write run manifest

    Do not implement a custom ITCH parser here.
    """
    raise NotImplementedError("Week 2 task: implement MeatPy sample pipeline step by step.")
