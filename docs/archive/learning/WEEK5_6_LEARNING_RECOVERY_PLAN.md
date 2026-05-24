# Week 5-6 Learning Recovery Plan

## Why This Exists

The Week 5-6 implementation moved too quickly. The code can stay, but it should now be used as a guided learning artifact instead of treated as work that was fully learned.

The goal is to rebuild understanding one checkpoint at a time.

## Learning Rule For The Recovery

Do not add new features during this recovery path.

For each checkpoint:

1. Read the relevant code.
2. Explain what problem it solves.
3. Predict what one test should prove.
4. Run or inspect that test.
5. Make a tiny learner-owned change only after the concept is understood.

## Checkpoint 1: Why order_events Exists

Read:

- `src/itch_data_pipeline/meatpy_integration/extract.py`
- `src/itch_data_pipeline/meatpy_integration/order_events.py`

Learn:

- `message_events` is a generic audit-style dataset.
- `order_events` is a derived event-level dataset.
- MeatPy still does the ITCH reading; this project maps MeatPy message objects into Parquet rows.

Question to answer:

Why is `order_events` separate from `message_events` instead of replacing it?

## Checkpoint 2: Mapping MeatPy Objects Without Writing A Parser

Read:

- `message_to_order_event_row`
- `ORDER_EVENT_TYPES_BY_CLASS`
- `tests/test_extract_order_events_sample.py`

Learn:

- The code uses `getattr` on MeatPy objects.
- It does not decode binary ITCH payloads manually.
- Missing fields become `None` because different message classes expose different attributes.

Question to answer:

Why is `AddOrderMPIDMessage` treated as an `add` event?

## Checkpoint 3: Manifests And Reproducibility

Read:

- `src/itch_data_pipeline/runner/extract_order_events_sample.py`
- `outputs/local/dataset=order_events/date=2019-12-30/symbol=ALL/manifest.json`

Learn:

- The manifest records input path, input hash, output path, scan bound, row count, timestamps, and status.
- The input SHA-256 proves which raw file produced the output.

Question to answer:

Why are both `input_file` and `input_sha256` useful?

## Checkpoint 4: Structural Validation

Read:

- `src/itch_data_pipeline/validation/order_events.py`
- `outputs/local/dataset=order_events/date=2019-12-30/symbol=ALL/validation_report.json`
- `tests/test_order_events_validation.py`

Learn:

- Validation checks objective structure, not full market correctness.
- The rules prove the output exists, has expected columns, has rows, matches the manifest, has event types, has expected order references, and has increasing sequence numbers.

Question to answer:

What does `order_refs_present` prove, and what does it still not prove?

## Checkpoint 5: DuckDB Analytics

Read:

- `src/itch_data_pipeline/analytics/order_events.py`
- `tests/test_order_events_analytics.py`

Learn:

- DuckDB queries Parquet directly.
- The analytics are summaries over generated artifacts, not hidden pipeline execution.

Question to answer:

Why is querying Parquet with DuckDB better here than loading the whole dataset into Streamlit?

## Checkpoint 6: Reports And Streamlit Boundaries

Read:

- `src/itch_data_pipeline/reporting/week6_report.py`
- `src/itch_data_pipeline/reporting/showcase_context.py`
- `app/streamlit_app.py`

Learn:

- The report turns artifacts into a professor-facing narrative.
- Streamlit only reads artifacts that already exist.
- Streamlit must not parse raw ITCH or run extraction.

Question to answer:

Where would you look to prove that Streamlit is not executing the pipeline?

## Checkpoint 7: HPC Execution And Proof

Read:

- `hpc/submit_week6_showcase.slurm`
- `docs/WEEK6_HPC_STATUS.md`
- `logs/hpc_week6_5386100.out`

Learn:

- The SLURM script runs the same CLI commands as local development.
- SLURM schedules the job on a compute node instead of running heavy work on the access node.
- Job `5386100` ran on `iris-111` and completed successfully.
- The strongest proof combines the SLURM job log, output row counts, validation reports, and generated report.

Question to answer:

Why is a successful HPC run stronger evidence than a local-only run?
