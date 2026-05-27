from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from itch_data_pipeline.analytics.lob_snapshots import lob_snapshot_summary
from itch_data_pipeline.analytics.message_events import message_type_counts
from itch_data_pipeline.analytics.order_events import order_event_summary
from itch_data_pipeline.manifests.manifest_writer import build_sample_manifest, write_manifest
from itch_data_pipeline.meatpy_integration.peek import summarize_itch50_messages
from itch_data_pipeline.meatpy_integration.probe import probe_meatpy
from itch_data_pipeline.reporting.week4_report import build_week4_showcase_report
from itch_data_pipeline.reporting.week6_report import build_week6_showcase_report
from itch_data_pipeline.reporting.week12_report import build_week12_final_report
from itch_data_pipeline.reporting.evidence_index import build_artifact_evidence_index
from itch_data_pipeline.runner.extract_itch50_sample import run_extract_itch50_sample
from itch_data_pipeline.runner.extract_lob_snapshots_sample import run_extract_lob_snapshots_sample
from itch_data_pipeline.runner.extract_order_events_sample import run_extract_order_events_sample
from itch_data_pipeline.runner.sample_peek_run import run_sample_peek
from itch_data_pipeline.safety.raw_data import scan_for_forbidden_artifacts
from itch_data_pipeline.utils.hashing import sha256_text
from itch_data_pipeline.validation.lob_snapshots import validate_lob_snapshots_partition
from itch_data_pipeline.validation.message_events import validate_message_events_partition
from itch_data_pipeline.validation.order_events import validate_order_events_partition


def healthcheck() -> None:
    print("itch-data-pipeline healthcheck: OK")
    print("Python package import: OK")
    print("Core starter utilities: OK")


def write_sample_manifest(output_path: str = "examples/generated_sample_manifest.json") -> None:
    manifest = build_sample_manifest()
    out = Path(output_path)
    write_manifest(manifest, out)
    print(f"Wrote sample manifest to {out}")
    print(f"Manifest JSON hash: {sha256_text(json.dumps(manifest, sort_keys=True))}")


def probe_meatpy_command() -> None:
    result = probe_meatpy()
    print(json.dumps(result, indent=2, sort_keys=True))


def peek_itch50(input_path: str, limit: int = 10) -> None:
    summary = summarize_itch50_messages(input_path, limit=limit)
    print(json.dumps(summary, indent=2, sort_keys=True))


def sample_peek_run(input_path: str, output_root: str = "outputs/local", limit: int = 10) -> None:
    result = run_sample_peek(input_path, output_root=output_root, limit=limit)
    print(json.dumps(result, indent=2, sort_keys=True))


def extract_itch50_sample(
    input_path: str,
    date: str,
    output_root: str = "outputs/local",
    max_messages: int = 100_000,
) -> None:
    result = run_extract_itch50_sample(
        input_path,
        date=date,
        output_root=output_root,
        max_messages=max_messages,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def extract_order_events_sample(
    input_path: str,
    date: str,
    output_root: str = "outputs/local",
    max_messages: int = 1_000_000,
) -> None:
    result = run_extract_order_events_sample(
        input_path,
        date=date,
        output_root=output_root,
        max_messages=max_messages,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def extract_lob_snapshots_sample(
    input_path: str,
    date: str,
    symbol: str,
    output_root: str = "outputs/local",
    max_messages: int | None = 1_000_000,
    until_eof: bool = False,
) -> None:
    result = run_extract_lob_snapshots_sample(
        input_path,
        date=date,
        symbol=symbol,
        output_root=output_root,
        max_messages=max_messages,
        until_eof=until_eof,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def query_message_types(output_root: str, date: str, symbol: str = "ALL", limit: int | None = None) -> None:
    result = message_type_counts(output_root, date=date, symbol=symbol, limit=limit)
    print(json.dumps(result, indent=2, sort_keys=True))


def query_order_event_summary(output_root: str, date: str, symbol: str = "ALL", limit: int = 10) -> None:
    result = order_event_summary(output_root, date=date, symbol=symbol, limit=limit)
    print(json.dumps(result, indent=2, sort_keys=True))


def query_lob_summary(output_root: str, date: str, symbol: str) -> None:
    result = lob_snapshot_summary(output_root, date=date, symbol=symbol)
    print(json.dumps(result, indent=2, sort_keys=True))


def validate_message_events(output_root: str, date: str, symbol: str = "ALL") -> None:
    result = validate_message_events_partition(output_root, date=date, symbol=symbol)
    print(json.dumps(result, indent=2, sort_keys=True))


def validate_order_events(output_root: str, date: str, symbol: str = "ALL") -> None:
    result = validate_order_events_partition(output_root, date=date, symbol=symbol)
    print(json.dumps(result, indent=2, sort_keys=True))


def validate_lob_snapshots(output_root: str, date: str, symbol: str) -> None:
    result = validate_lob_snapshots_partition(output_root, date=date, symbol=symbol)
    print(json.dumps(result, indent=2, sort_keys=True))


def write_week4_report(
    output_root: str,
    date: str,
    symbol: str = "ALL",
    report_path: str = "reports/week4_showcase.md",
    top_n: int = 10,
) -> None:
    result = build_week4_showcase_report(
        output_root=output_root,
        date=date,
        symbol=symbol,
        report_path=report_path,
        top_n=top_n,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def write_week6_report(
    output_root: str,
    date: str,
    symbol: str = "ALL",
    report_path: str = "reports/week6_showcase.md",
    top_n: int = 10,
) -> None:
    result = build_week6_showcase_report(
        output_root=output_root,
        date=date,
        symbol=symbol,
        report_path=report_path,
        top_n=top_n,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def write_event_pipeline_report(
    output_root: str,
    date: str,
    symbol: str = "ALL",
    report_path: str = "reports/event_pipeline_showcase.md",
    top_n: int = 10,
) -> None:
    result = build_week6_showcase_report(
        output_root=output_root,
        date=date,
        symbol=symbol,
        report_path=report_path,
        top_n=top_n,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def write_week12_report(
    proof_root: str = "logs",
    report_path: str = "reports/final_evidence_report.md",
) -> None:
    result = build_week12_final_report(
        proof_root=proof_root,
        report_path=report_path,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def write_artifact_evidence_index(
    proof_root: str = "logs",
    report_path: str = "reports/artifact_evidence_index.md",
) -> None:
    result = build_artifact_evidence_index(
        proof_root=proof_root,
        report_path=report_path,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def check_raw_data_safety(repo_root: str = ".") -> None:
    """Scan *repo_root* for forbidden raw-data artifacts and print JSON.

    Exits with code 1 if any violations are found so CI can use this as a gate.
    """
    result = scan_for_forbidden_artifacts(repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "passed":
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Starter CLI for ITCH data pipeline.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("healthcheck", help="Run local project healthcheck.")
    sub.add_parser("probe-meatpy", help="Check whether MeatPy can be imported.")

    peek_parser = sub.add_parser("peek-itch50", help="Read the first ITCH 5.0 messages with MeatPy.")
    peek_parser.add_argument("input", help="Path to a MeatPy-readable ITCH 5.0 file.")
    peek_parser.add_argument("--limit", type=int, default=10, help="Number of messages to read.")

    sample_peek_parser = sub.add_parser(
        "sample-peek-run",
        help="Read a tiny ITCH 5.0 sample and write summary plus manifest JSON.",
    )
    sample_peek_parser.add_argument("--input", required=True, help="Path to a MeatPy-readable ITCH 5.0 file.")
    sample_peek_parser.add_argument("--limit", type=int, default=10, help="Number of messages to read.")
    sample_peek_parser.add_argument("--output-root", default="outputs/local", help="Root directory for outputs.")

    extract_parser = sub.add_parser(
        "extract-itch50-sample",
        help="Write a bounded ITCH 5.0 message_events Parquet dataset plus manifest.",
    )
    extract_parser.add_argument("--input", required=True, help="Path to a MeatPy-readable ITCH 5.0 file.")
    extract_parser.add_argument("--date", required=True, help="Trading date partition for this input file.")
    extract_parser.add_argument("--max-messages", type=int, default=100_000, help="Maximum messages to extract.")
    extract_parser.add_argument("--output-root", default="outputs/local", help="Root directory for outputs.")

    order_extract_parser = sub.add_parser(
        "extract-order-events-sample",
        help="Write a bounded ITCH 5.0 order_events Parquet dataset plus manifest.",
    )
    order_extract_parser.add_argument("--input", required=True, help="Path to a MeatPy-readable ITCH 5.0 file.")
    order_extract_parser.add_argument("--date", required=True, help="Trading date partition for this input file.")
    order_extract_parser.add_argument("--max-messages", type=int, default=1_000_000, help="Maximum messages to scan.")
    order_extract_parser.add_argument("--output-root", default="outputs/local", help="Root directory for outputs.")

    lob_extract_parser = sub.add_parser(
        "extract-lob-snapshots-sample",
        help="Write a bounded ITCH 5.0 lob_snapshots Parquet dataset plus manifest.",
    )
    lob_extract_parser.add_argument("--input", required=True, help="Path to a MeatPy-readable ITCH 5.0 file.")
    lob_extract_parser.add_argument("--date", required=True, help="Trading date partition for this input file.")
    lob_extract_parser.add_argument("--symbol", required=True, help="Single symbol to reconstruct, e.g. SPY.")
    lob_extract_parser.add_argument("--max-messages", type=int, default=1_000_000, help="Maximum messages to scan.")
    lob_extract_parser.add_argument(
        "--until-eof",
        action="store_true",
        help="Scan until the ITCH reader reaches EOF instead of stopping at --max-messages.",
    )
    lob_extract_parser.add_argument("--output-root", default="outputs/local", help="Root directory for outputs.")

    query_parser = sub.add_parser(
        "query-message-types",
        help="Query message type counts from message_events Parquet with DuckDB.",
    )
    query_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    query_parser.add_argument("--date", required=True, help="Date partition to query.")
    query_parser.add_argument("--symbol", default="ALL", help="Symbol partition to query.")
    query_parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of rows to return.")

    order_query_parser = sub.add_parser(
        "query-order-event-summary",
        help="Query order_events Parquet summaries with DuckDB.",
    )
    order_query_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    order_query_parser.add_argument("--date", required=True, help="Date partition to query.")
    order_query_parser.add_argument("--symbol", default="ALL", help="Symbol partition to query.")
    order_query_parser.add_argument("--limit", type=int, default=10, help="Maximum rows for ranked summary tables.")

    lob_query_parser = sub.add_parser(
        "query-lob-summary",
        help="Query lob_snapshots Parquet summary with DuckDB.",
    )
    lob_query_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    lob_query_parser.add_argument("--date", required=True, help="Date partition to query.")
    lob_query_parser.add_argument("--symbol", required=True, help="Symbol partition to query.")

    validate_parser = sub.add_parser(
        "validate-message-events",
        help="Run structural validation on a message_events Parquet partition.",
    )
    validate_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    validate_parser.add_argument("--date", required=True, help="Date partition to validate.")
    validate_parser.add_argument("--symbol", default="ALL", help="Symbol partition to validate.")

    order_validate_parser = sub.add_parser(
        "validate-order-events",
        help="Run structural validation on an order_events Parquet partition.",
    )
    order_validate_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    order_validate_parser.add_argument("--date", required=True, help="Date partition to validate.")
    order_validate_parser.add_argument("--symbol", default="ALL", help="Symbol partition to validate.")

    lob_validate_parser = sub.add_parser(
        "validate-lob-snapshots",
        help="Run structural validation on a lob_snapshots Parquet partition.",
    )
    lob_validate_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    lob_validate_parser.add_argument("--date", required=True, help="Date partition to validate.")
    lob_validate_parser.add_argument("--symbol", required=True, help="Symbol partition to validate.")

    report_parser = sub.add_parser(
        "write-week4-report",
        help="Write a legacy message-event Markdown showcase report from existing artifacts.",
    )
    report_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    report_parser.add_argument("--date", required=True, help="Date partition to report.")
    report_parser.add_argument("--symbol", default="ALL", help="Symbol partition to report.")
    report_parser.add_argument("--report-path", default="reports/week4_showcase.md", help="Markdown report path.")
    report_parser.add_argument("--top-n", type=int, default=10, help="Number of message type rows to include.")

    week6_report_parser = sub.add_parser(
        "write-week6-report",
        help="Write a legacy event-pipeline Markdown showcase report from existing artifacts.",
    )
    week6_report_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    week6_report_parser.add_argument("--date", required=True, help="Date partition to report.")
    week6_report_parser.add_argument("--symbol", default="ALL", help="Symbol partition to report.")
    week6_report_parser.add_argument("--report-path", default="reports/week6_showcase.md", help="Markdown report path.")
    week6_report_parser.add_argument("--top-n", type=int, default=10, help="Number of ranked rows to include.")

    event_report_parser = sub.add_parser(
        "write-event-pipeline-report",
        help="Write a Markdown report for message_events and order_events artifacts.",
    )
    event_report_parser.add_argument("--output-root", default="outputs/local", help="Root directory containing outputs.")
    event_report_parser.add_argument("--date", required=True, help="Date partition to report.")
    event_report_parser.add_argument("--symbol", default="ALL", help="Symbol partition to report.")
    event_report_parser.add_argument(
        "--report-path",
        default="reports/event_pipeline_showcase.md",
        help="Markdown report path.",
    )
    event_report_parser.add_argument("--top-n", type=int, default=10, help="Number of ranked rows to include.")

    week12_report_parser = sub.add_parser(
        "write-week12-report",
        help="Write the final evidence report from copied proof artifacts.",
    )
    week12_report_parser.add_argument("--proof-root", default="logs", help="Directory containing copied proof artifacts.")
    week12_report_parser.add_argument(
        "--report-path",
        default="reports/final_evidence_report.md",
        help="Markdown report path.",
    )

    evidence_index_parser = sub.add_parser(
        "write-artifact-evidence-index",
        help="Write a Markdown evidence index from copied proof artifacts.",
    )
    evidence_index_parser.add_argument("--proof-root", default="logs", help="Directory containing copied proof artifacts.")
    evidence_index_parser.add_argument(
        "--report-path",
        default="reports/artifact_evidence_index.md",
        help="Markdown report path.",
    )

    manifest_parser = sub.add_parser("write-sample-manifest", help="Write sample manifest JSON.")
    manifest_parser.add_argument("--output", default="examples/generated_sample_manifest.json")

    safety_parser = sub.add_parser(
        "check-raw-data-safety",
        help="Scan the repo for forbidden raw-data artifacts (raw ITCH .gz, large Parquet outputs).",
    )
    safety_parser.add_argument(
        "--repo-root",
        default=".",
        help="Root directory to scan (default: current working directory).",
    )

    args = parser.parse_args()

    if args.command == "healthcheck":
        healthcheck()
    elif args.command == "probe-meatpy":
        probe_meatpy_command()
    elif args.command == "peek-itch50":
        peek_itch50(args.input, limit=args.limit)
    elif args.command == "sample-peek-run":
        sample_peek_run(args.input, output_root=args.output_root, limit=args.limit)
    elif args.command == "extract-itch50-sample":
        extract_itch50_sample(
            args.input,
            date=args.date,
            output_root=args.output_root,
            max_messages=args.max_messages,
        )
    elif args.command == "extract-order-events-sample":
        extract_order_events_sample(
            args.input,
            date=args.date,
            output_root=args.output_root,
            max_messages=args.max_messages,
        )
    elif args.command == "extract-lob-snapshots-sample":
        extract_lob_snapshots_sample(
            args.input,
            date=args.date,
            symbol=args.symbol,
            output_root=args.output_root,
            max_messages=args.max_messages,
            until_eof=args.until_eof,
        )
    elif args.command == "query-message-types":
        query_message_types(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
            limit=args.limit,
        )
    elif args.command == "query-order-event-summary":
        query_order_event_summary(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
            limit=args.limit,
        )
    elif args.command == "query-lob-summary":
        query_lob_summary(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
        )
    elif args.command == "validate-message-events":
        validate_message_events(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
        )
    elif args.command == "validate-order-events":
        validate_order_events(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
        )
    elif args.command == "validate-lob-snapshots":
        validate_lob_snapshots(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
        )
    elif args.command == "write-week4-report":
        write_week4_report(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
            report_path=args.report_path,
            top_n=args.top_n,
        )
    elif args.command == "write-week6-report":
        write_week6_report(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
            report_path=args.report_path,
            top_n=args.top_n,
        )
    elif args.command == "write-event-pipeline-report":
        write_event_pipeline_report(
            args.output_root,
            date=args.date,
            symbol=args.symbol,
            report_path=args.report_path,
            top_n=args.top_n,
        )
    elif args.command == "write-week12-report":
        write_week12_report(
            proof_root=args.proof_root,
            report_path=args.report_path,
        )
    elif args.command == "write-artifact-evidence-index":
        write_artifact_evidence_index(
            proof_root=args.proof_root,
            report_path=args.report_path,
        )
    elif args.command == "write-sample-manifest":
        write_sample_manifest(args.output)
    elif args.command == "check-raw-data-safety":
        check_raw_data_safety(repo_root=args.repo_root)


if __name__ == "__main__":
    main()
