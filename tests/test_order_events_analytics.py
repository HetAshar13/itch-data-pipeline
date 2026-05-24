import json
from pathlib import Path

import pandas as pd
import pytest

from itch_data_pipeline import cli
from itch_data_pipeline.analytics.order_events import order_event_summary
from itch_data_pipeline.cli import query_order_event_summary
from itch_data_pipeline.meatpy_integration.order_events import ORDER_EVENT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path


def write_order_events_fixture(output_root: Path, date: str = "2019-12-30") -> Path:
    out_dir = partition_path(output_root, "order_events", date, "ALL")
    out_dir.mkdir(parents=True)
    parquet_path = out_dir / "part-000.parquet"
    pd.DataFrame(
        [
            {
                "sequence_number": 1,
                "event_type": "add",
                "message_type": "A",
                "message_class": "AddOrderMessage",
                "stock_locate": 1,
                "tracking_number": 0,
                "timestamp_ns": 100,
                "order_ref": 10,
                "original_ref": None,
                "new_ref": None,
                "side": "B",
                "shares": 100,
                "price": 123400,
                "canceled_shares": None,
                "match_number": None,
                "stock": "AAPL",
                "description": "Add Order Message",
            },
            {
                "sequence_number": 2,
                "event_type": "add",
                "message_type": "A",
                "message_class": "AddOrderMessage",
                "stock_locate": 1,
                "tracking_number": 0,
                "timestamp_ns": 101,
                "order_ref": 11,
                "original_ref": None,
                "new_ref": None,
                "side": "S",
                "shares": 50,
                "price": 123500,
                "canceled_shares": None,
                "match_number": None,
                "stock": "AAPL",
                "description": "Add Order Message",
            },
            {
                "sequence_number": 3,
                "event_type": "cancel",
                "message_type": "X",
                "message_class": "OrderCancelMessage",
                "stock_locate": 1,
                "tracking_number": 0,
                "timestamp_ns": 102,
                "order_ref": 10,
                "original_ref": None,
                "new_ref": None,
                "side": None,
                "shares": None,
                "price": None,
                "canceled_shares": 10,
                "match_number": None,
                "stock": None,
                "description": "Order Cancel Message",
            },
        ],
        columns=ORDER_EVENT_COLUMNS,
    ).to_parquet(parquet_path, index=False)
    return parquet_path


def test_order_event_summary_queries_partitioned_parquet(tmp_path: Path):
    write_order_events_fixture(tmp_path)

    result = order_event_summary(tmp_path, date="2019-12-30", limit=10)

    assert result["event_counts"] == [
        {"event_type": "add", "row_count": 2},
        {"event_type": "cancel", "row_count": 1},
    ]
    assert result["side_counts"] == [
        {"side": "B", "row_count": 1, "total_shares": 100},
        {"side": "S", "row_count": 1, "total_shares": 50},
    ]
    assert result["top_stocks_by_adds"] == [
        {"stock": "AAPL", "add_count": 2, "total_add_shares": 150}
    ]
    assert result["activity_counts"] == {"add": 2, "cancel": 1}


def test_order_event_summary_raises_for_missing_partition(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="order_events Parquet not found"):
        order_event_summary(tmp_path, date="2019-12-30")


def test_query_order_event_summary_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "order_event_summary",
        lambda output_root, date, symbol="ALL", limit=10: {
            "event_counts": [{"event_type": "add", "row_count": 2}],
            "side_counts": [],
            "top_stocks_by_adds": [],
            "activity_counts": {"add": 2},
        },
    )

    query_order_event_summary("outputs/local", date="2019-12-30")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["event_counts"][0]["event_type"] == "add"
    assert result["activity_counts"]["add"] == 2
