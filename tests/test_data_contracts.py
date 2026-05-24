from pathlib import Path

from itch_data_pipeline.meatpy_integration.extract import MESSAGE_EVENT_COLUMNS
from itch_data_pipeline.meatpy_integration.lob_snapshots import LOB_SNAPSHOT_COLUMNS
from itch_data_pipeline.meatpy_integration.order_events import ORDER_EVENT_COLUMNS


def test_data_contracts_document_all_dataset_columns():
    content = Path("docs/DATA_CONTRACTS.md").read_text(encoding="utf-8")

    for column in MESSAGE_EVENT_COLUMNS:
        assert f"`{column}`" in content

    for column in ORDER_EVENT_COLUMNS:
        assert f"`{column}`" in content

    for column in LOB_SNAPSHOT_COLUMNS:
        if "_2_" in column or "_3_" in column or "_4_" in column:
            continue
        assert f"`{column}`" in content


def test_data_contracts_document_raw_price_policy_and_validation_boundary():
    content = Path("docs/DATA_CONTRACTS.md").read_text(encoding="utf-8")

    assert "Raw Nasdaq ITCH data stays outside Git" in content
    assert "raw integer price units" in content
    assert "does not prove complete market microstructure correctness" in content
    assert "outputs/<root>/dataset=lob_snapshots/date=<date>/symbol=<symbol>/part-000.parquet" in content
