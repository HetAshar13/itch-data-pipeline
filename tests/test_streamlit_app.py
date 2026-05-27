import json
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from itch_data_pipeline.manifests.manifest_writer import write_manifest
from itch_data_pipeline.meatpy_integration.extract import MESSAGE_EVENT_COLUMNS
from itch_data_pipeline.meatpy_integration.order_events import ORDER_EVENT_COLUMNS
from itch_data_pipeline.utils.paths import partition_path


def write_app_artifacts(output_root: Path, date: str = "2019-12-30") -> None:
    message_dir = partition_path(output_root, "message_events", date, "ALL")
    order_dir = partition_path(output_root, "order_events", date, "ALL")
    message_dir.mkdir(parents=True)
    order_dir.mkdir(parents=True)

    pd.DataFrame(
        [
            {
                "sequence_number": 1,
                "message_type": "A",
                "message_class": "AddOrderMessage",
                "stock_locate": 1,
                "tracking_number": 0,
                "timestamp_ns": 123,
                "stock": "AAPL",
                "description": "Add Order Message",
            }
        ],
        columns=MESSAGE_EVENT_COLUMNS,
    ).to_parquet(message_dir / "part-000.parquet", index=False)
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "row_counts": {"message_events": 1},
            "status": "success",
        },
        message_dir / "manifest.json",
    )
    (message_dir / "validation_report.json").write_text(
        json.dumps({"status": "passed", "rules_failed": 0, "findings": []}),
        encoding="utf-8",
    )

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
    ).to_parquet(order_dir / "part-000.parquet", index=False)
    write_manifest(
        {
            "input_file": "data/sample.gz",
            "input_sha256": "abc123",
            "row_counts": {"order_events": 1},
            "status": "success",
        },
        order_dir / "manifest.json",
    )
    (order_dir / "validation_report.json").write_text(
        json.dumps({"status": "passed", "rules_failed": 0, "findings": []}),
        encoding="utf-8",
    )


def test_streamlit_app_renders_week6_sections(tmp_path: Path):
    write_app_artifacts(tmp_path)
    app = AppTest.from_file("app/streamlit_app.py")

    app.run(timeout=30)
    app.text_input[0].input(str(tmp_path))
    app.run(timeout=30)

    assert len(app.exception) == 0
    assert "Order Events" in [subheader.value for subheader in app.subheader]
    assert "Order events" in [metric.label for metric in app.metric]
