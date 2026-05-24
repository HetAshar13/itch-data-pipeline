import json
from pathlib import Path

from itch_data_pipeline.runner import sample_peek_run


class FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, *args):
        self.messages.append(message % args)


def test_run_sample_peek_writes_summary_and_manifest(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    def fake_summarize(input_file: Path, limit: int = 10):
        return {
            "input_file": str(input_file),
            "limit": limit,
            "messages_read": 2,
            "message_type_counts": {"R": 1, "S": 1},
            "message_class_counts": {
                "StockDirectoryMessage": 1,
                "SystemEventMessage": 1,
            },
        }

    monkeypatch.setattr(sample_peek_run, "summarize_itch50_messages", fake_summarize)
    monkeypatch.setattr(
        sample_peek_run,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = sample_peek_run.run_sample_peek(input_path, output_root=output_root, limit=2)

    summary_path = Path(result["summary_path"])
    manifest_path = Path(result["manifest_path"])
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert summary_path.exists()
    assert manifest_path.exists()
    assert summary["messages_read"] == 2
    assert manifest["output_paths"] == [str(summary_path)]
    assert manifest["row_counts"]["messages_read"] == 2
    assert manifest["meatpy_version"] == "test-version"
    assert manifest["status"] == "success"
    assert manifest["validation_summary"]["status"] == "not_run"
    assert manifest["validation_summary"]["rules_run"] == 0
    assert manifest["validation_summary"]["rules_failed"] == 0


def test_run_sample_peek_uses_message_peek_partition(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")

    monkeypatch.setattr(
        sample_peek_run,
        "summarize_itch50_messages",
        lambda input_file, limit=10: {
            "input_file": str(input_file),
            "limit": limit,
            "messages_read": 1,
            "message_type_counts": {"S": 1},
            "message_class_counts": {"SystemEventMessage": 1},
        },
    )
    monkeypatch.setattr(
        sample_peek_run,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    result = sample_peek_run.run_sample_peek(input_path, output_root=output_root, limit=1)

    assert Path(result["summary_path"]).parent == (
        output_root / "dataset=message_peek" / "date=unknown" / "symbol=ALL"
    )


def test_run_sample_peek_logs_start_and_outputs(monkeypatch, tmp_path: Path):
    input_path = tmp_path / "sample.itch50.gz"
    output_root = tmp_path / "outputs"
    input_path.write_text("small sample bytes", encoding="utf-8")
    logger = FakeLogger()

    monkeypatch.setattr(sample_peek_run, "get_logger", lambda name: logger)
    monkeypatch.setattr(
        sample_peek_run,
        "summarize_itch50_messages",
        lambda input_file, limit=10: {
            "input_file": str(input_file),
            "limit": limit,
            "messages_read": 1,
            "message_type_counts": {"S": 1},
            "message_class_counts": {"SystemEventMessage": 1},
        },
    )
    monkeypatch.setattr(
        sample_peek_run,
        "probe_meatpy",
        lambda: {"installed": True, "version": "test-version"},
    )

    sample_peek_run.run_sample_peek(input_path, output_root=output_root, limit=1)

    assert any("Starting sample peek run" in message for message in logger.messages)
    assert any("Wrote sample peek summary" in message for message in logger.messages)
    assert any("Wrote sample peek manifest" in message for message in logger.messages)
