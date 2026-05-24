from pathlib import Path

import json
import pandas as pd
import pytest

from itch_data_pipeline import cli
from itch_data_pipeline.analytics.lob_snapshots import lob_snapshot_summary
from itch_data_pipeline.cli import query_lob_summary
from itch_data_pipeline.meatpy_integration.lob_snapshots import LOB_SNAPSHOT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path


def write_lob_snapshots_fixture(output_root: Path, date: str = "2019-12-30", symbol: str = "SPY") -> Path:
    out_dir = partition_path(output_root, "lob_snapshots", date, symbol)
    out_dir.mkdir(parents=True)
    parquet_path = out_dir / "part-000.parquet"

    rows = []
    for row in [
        {
            "snapshot_number": 1,
            "sequence_number": 10,
            "timestamp_ns": 100,
            "symbol": "SPY",
            "source_message_type": "A",
            "source_message_class": "AddOrderMessage",
            "bid_price_1_raw": 100,
            "bid_size_1": 200,
        },
        {
            "snapshot_number": 2,
            "sequence_number": 11,
            "timestamp_ns": 101,
            "symbol": "SPY",
            "source_message_type": "A",
            "source_message_class": "AddOrderMessage",
            "bid_price_1_raw": 100,
            "bid_size_1": 200,
            "ask_price_1_raw": 105,
            "ask_size_1": 300,
            "spread_1_raw": 5,
            "mid_price_1_raw": 102.5,
            "level1_imbalance": -0.2,
        },
        {
            "snapshot_number": 3,
            "sequence_number": 12,
            "timestamp_ns": 102,
            "symbol": "SPY",
            "source_message_type": "X",
            "source_message_class": "OrderCancelMessage",
            "bid_price_1_raw": 99,
            "bid_size_1": 100,
            "ask_price_1_raw": 107,
            "ask_size_1": 300,
            "spread_1_raw": 8,
            "mid_price_1_raw": 103.0,
            "level1_imbalance": -0.5,
        },
    ]:
        base = {column: None for column in LOB_SNAPSHOT_COLUMNS}
        base.update(row)
        rows.append(base)

    pd.DataFrame(rows, columns=LOB_SNAPSHOT_COLUMNS).to_parquet(parquet_path, index=False)
    return parquet_path


def test_lob_snapshot_summary_queries_partitioned_parquet(tmp_path: Path):
    write_lob_snapshots_fixture(tmp_path)

    result = lob_snapshot_summary(tmp_path, date="2019-12-30", symbol="SPY")

    assert result["symbol"] == "SPY"
    assert result["snapshot_count"] == 3
    assert result["first_timestamp_ns"] == 100
    assert result["last_timestamp_ns"] == 102
    assert result["two_sided_snapshot_count"] == 2
    assert result["two_sided_snapshot_percent"] == pytest.approx(66.6666667)
    assert result["avg_spread_1_raw"] == pytest.approx(6.5)
    assert result["median_spread_1_raw"] == pytest.approx(6.5)
    assert result["min_spread_1_raw"] == 5
    assert result["max_spread_1_raw"] == 8
    assert result["avg_level1_imbalance"] == pytest.approx(-0.35)


def test_lob_snapshot_summary_raises_for_missing_partition(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="lob_snapshots Parquet not found"):
        lob_snapshot_summary(tmp_path, date="2019-12-30", symbol="SPY")


def test_query_lob_summary_prints_json(capsys, monkeypatch):
    monkeypatch.setattr(
        cli,
        "lob_snapshot_summary",
        lambda output_root, date, symbol: {
            "symbol": symbol,
            "snapshot_count": 3,
            "two_sided_snapshot_percent": 66.6667,
        },
    )

    query_lob_summary("outputs/local", date="2019-12-30", symbol="SPY")

    captured = capsys.readouterr()
    result = json.loads(captured.out)

    assert result["symbol"] == "SPY"
    assert result["snapshot_count"] == 3
    assert result["two_sided_snapshot_percent"] == 66.6667
