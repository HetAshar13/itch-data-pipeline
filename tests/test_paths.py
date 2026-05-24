from itch_data_pipeline.utils.paths import partition_path


def test_partition_path():
    path = partition_path("outputs", "order_events", "2026-05-01", "AAPL")
    assert str(path).replace("\\", "/") == "outputs/dataset=order_events/date=2026-05-01/symbol=AAPL"


def test_partition_path_changes_symbol_partition():
    path = partition_path("outputs", "order_events", "2026-05-01", "MSFT")
    assert str(path).replace("\\", "/") == "outputs/dataset=order_events/date=2026-05-01/symbol=MSFT"
