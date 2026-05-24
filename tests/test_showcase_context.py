import json
from pathlib import Path

import pandas as pd

from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.extract import MESSAGE_EVENT_COLUMNS
from itch_data_pipeline.meatpy_integration.order_events import ORDER_EVENT_COLUMNS
from itch_data_pipeline.reporting import showcase_context
from itch_data_pipeline.utils.paths import partition_path


def write_showcase_artifacts(output_root: Path, date: str = "2019-12-30") -> None:
    out_dir = partition_path(output_root, "message_events", date, "ALL")
    out_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "sequence_number": 1,
                "message_type": "S",
                "message_class": "SystemEventMessage",
                "stock_locate": 0,
                "tracking_number": 0,
                "timestamp_ns": 123,
                "stock": None,
                "description": "System Event Message",
            },
            {
                "sequence_number": 2,
                "message_type": "R",
                "message_class": "StockDirectoryMessage",
                "stock_locate": 1,
                "tracking_number": 0,
                "timestamp_ns": 456,
                "stock": "A",
                "description": "Stock Directory Message",
            },
        ],
        columns=MESSAGE_EVENT_COLUMNS,
    ).to_parquet(out_dir / "part-000.parquet", index=False)
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "row_counts": {"message_events": 2},
            "status": "success",
        },
        out_dir / "manifest.json",
    )
    (out_dir / "validation_report.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "rules_failed": 0,
                "findings": [
                    {
                        "rule_name": "row_count_positive",
                        "status": "passed",
                        "severity": "high",
                        "violations": 0,
                        "message": "Row count is 2.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def write_order_showcase_artifacts(output_root: Path, date: str = "2019-12-30") -> None:
    out_dir = partition_path(output_root, "order_events", date, "ALL")
    out_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "sequence_number": 1,
                "event_type": "add",
                "message_type": "A",
                "message_class": "AddOrderMessage",
                "stock_locate": 1,
                "tracking_number": 0,
                "timestamp_ns": 123,
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
            }
        ],
        columns=ORDER_EVENT_COLUMNS,
    ).to_parquet(out_dir / "part-000.parquet", index=False)
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "row_counts": {"order_events": 1},
            "status": "success",
        },
        out_dir / "manifest.json",
    )
    (out_dir / "validation_report.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "rules_failed": 0,
                "findings": [],
            }
        ),
        encoding="utf-8",
    )


def test_load_showcase_context_reads_pipeline_artifacts(tmp_path: Path):
    write_showcase_artifacts(tmp_path)

    context = showcase_context.load_showcase_context(
        output_root=tmp_path,
        date="2019-12-30",
        top_n=2,
        sample_rows=1,
    )

    assert context["manifest"]["status"] == "success"
    assert context["validation"]["status"] == "passed"
    assert len(context["top_message_types"]) == 2
    assert len(context["sample_rows"]) == 1
    assert context["sample_rows"][0]["message_type"] == "S"
    assert context["order_events"]["available"] is False


def test_load_showcase_context_reads_optional_order_events(tmp_path: Path):
    write_showcase_artifacts(tmp_path)
    write_order_showcase_artifacts(tmp_path)

    context = showcase_context.load_showcase_context(
        output_root=tmp_path,
        date="2019-12-30",
        top_n=2,
        sample_rows=1,
    )

    order_events = context["order_events"]
    assert order_events["available"] is True
    assert order_events["manifest"]["row_counts"]["order_events"] == 1
    assert order_events["validation"]["status"] == "passed"
    assert order_events["summary"]["event_counts"] == [{"event_type": "add", "row_count": 1}]
    assert order_events["sample_rows"][0]["event_type"] == "add"
