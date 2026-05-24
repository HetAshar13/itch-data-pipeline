import json
from pathlib import Path

import pandas as pd
import pytest

from itch_data_pipeline import cli
from itch_data_pipeline.analytics.message_events import message_type_counts
from itch_data_pipeline.cli import query_message_types
from itch_data_pipeline.utils.paths import partition_path


def write_message_events_fixture(output_root: Path, date: str = "2019-12-30") -> Path:
    out_dir = partition_path(output_root, "message_events", date, "ALL")
    out_dir.mkdir(parents=True)
    parquet_path = out_dir / "part-000.parquet"
    pd.DataFrame(
        [
            {"message_type": "R", "message_class": "StockDirectoryMessage"},
            {"message_type": "R", "message_class": "StockDirectoryMessage"},
            {"message_type": "S", "message_class": "SystemEventMessage"},
        ]
    ).to_parquet(parquet_path, index=False)
    return parquet_path


def test_message_type_counts_queries_partitioned_parquet(tmp_path: Path):
    write_message_events_fixture(tmp_path)

    result = message_type_counts(tmp_path, date="2019-12-30")

    assert result == [
        {
            "message_type": "R",
            "message_class": "StockDirectoryMessage",
            "row_count": 2,
        },
        {
            "message_type": "S",
            "message_class": "SystemEventMessage",
            "row_count": 1,
        },
    ]


def test_message_type_counts_raises_for_missing_partition(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="message_events Parquet not found"):
        message_type_counts(tmp_path, date="2019-12-30")


def test_query_message_types_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "message_type_counts",
        lambda output_root, date, symbol="ALL", limit=None: [
            {
                "message_type": "R",
                "message_class": "StockDirectoryMessage",
                "row_count": 2,
            }
        ],
    )

    query_message_types("outputs/local", date="2019-12-30")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result[0]["message_type"] == "R"
    assert result[0]["row_count"] == 2
