# Week 4 Professor Demo

## Goal

Show a reliable data engineering path over a real Nasdaq BX ITCH sample without claiming full market reconstruction.

## Demo Order

1. Open `reports/week4_showcase.md`.
2. Show the generated artifacts under `outputs/local/dataset=message_events/date=2019-12-30/symbol=ALL/`.
3. Open the Streamlit app with:

```powershell
streamlit run app/streamlit_app.py
```

4. Walk through the Streamlit sections:

- Run metadata
- Top message types
- Structural validation findings
- Sample message events
- Current boundaries

## Talk Track

This project uses MeatPy for ITCH reading instead of writing a custom parser. The project work is the engineering layer around that parser: bounded extraction, partitioned Parquet output, run manifests, structural validation, and DuckDB queries.

The current sample run extracts `100000` messages from a real Nasdaq BX ITCH file into `message_events` Parquet. The manifest records the input file, SHA-256 hash, row count, schema version, timestamps, and run status. The validation report checks that the Parquet file exists, expected columns are present, rows were written, and the manifest count matches the Parquet count.

DuckDB then queries the Parquet output directly to summarize message types. Streamlit only presents those existing artifacts; it does not parse raw ITCH data or execute the pipeline.

## What To Emphasize

- MeatPy handles ITCH message reading.
- Parquet makes the output queryable and efficient for later batch work.
- The manifest makes runs reproducible and inspectable.
- Validation catches structural pipeline failures before presentation.
- DuckDB proves the output is usable analytical data.
- Streamlit is intentionally a thin presentation layer.

## Honest Boundaries

- This does not prove full order book correctness.
- This does not implement full symbol/day processing.
- This does not run on SLURM yet.
- This does not add Spark, Airflow, Kafka, Snowflake, ML, or a large dashboard.

## Likely Questions

**Why not write a custom ITCH parser?**

Because the learning goal is data engineering around reliable market data processing. MeatPy already handles ITCH message reading, so this project focuses on reproducible outputs, validation, and queryable artifacts.

**What does validation prove?**

It proves the structural output is present, shaped as expected, non-empty, and consistent with the manifest row count. It does not prove market microstructure correctness.

**Why Streamlit?**

Streamlit makes the existing artifacts easier to inspect in a demo. It is not part of the pipeline execution path.

