from pathlib import Path

import pytest

from itch_data_pipeline.meatpy_integration import peek


class FakeSystemEventMessage:
    type = b"S"


class FakeStockDirectoryMessage:
    type = b"R"


class FakeReader:
    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        return iter(
            [
                FakeSystemEventMessage(),
                FakeStockDirectoryMessage(),
                FakeStockDirectoryMessage(),
            ]
        )

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_summarize_itch50_messages_counts_first_messages(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(peek, "ITCH50MessageReader", FakeReader)
    input_path = tmp_path / "sample.itch50.gz"

    summary = peek.summarize_itch50_messages(input_path, limit=2)

    assert summary["input_file"] == str(input_path)
    assert summary["limit"] == 2
    assert summary["messages_read"] == 2
    assert summary["message_type_counts"] == {"R": 1, "S": 1}
    assert summary["message_class_counts"] == {
        "FakeStockDirectoryMessage": 1,
        "FakeSystemEventMessage": 1,
    }


def test_summarize_itch50_messages_rejects_non_positive_limit(tmp_path: Path):
    with pytest.raises(ValueError, match="limit must be at least 1"):
        peek.summarize_itch50_messages(tmp_path / "sample.itch50.gz", limit=0)
