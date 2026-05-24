# Interview Notes

## Week 3 Step 1 — First Parquet output foundation

**What was built:**

- A bounded ITCH 5.0 extraction path that reads MeatPy message objects and writes a `message_events` Parquet dataset.
- A manifest-backed run that records the input file, SHA-256, output Parquet path, row count, MeatPy probe result, timestamps, and validation status.

**Why it matters for data engineering:**

This step turns a raw market data feed into a structured, queryable dataset while preserving reproducibility metadata. It shows the difference between parsing data and engineering a reliable pipeline around parsed data.

**Design decisions:**

- MeatPy remains responsible for reading ITCH messages.
- The first Parquet schema is intentionally generic: sequence number, message type, class, stock locate, tracking number, timestamp, stock, and description.
- The command is bounded by `--max-messages` so local development does not accidentally process an entire large ITCH file.
- Validation is honestly marked `not_run` until real validation rules exist.

**Tradeoffs:**

- A generic `message_events` dataset is less detailed than full order-event extraction, but it is stable and easy to defend.
- Nullable fields are acceptable because different ITCH message types expose different attributes.
- Full order book reconstruction is deferred until the data layout and run metadata are reliable.

**Questions I should be able to answer:**

- Why did you use MeatPy instead of writing your own ITCH parser?
- Why is Parquet a better first structured output than CSV?
- What does `--max-messages` protect you from?
- Why does the manifest store both the input file path and input SHA-256?
- Why is validation marked `not_run` instead of `passed`?

**Strong answer in this project context:**

In Week 3, I moved from a read-only MeatPy peek to a bounded Parquet extraction. I deliberately started with a generic `message_events` dataset because it let me prove streaming reads, schema design, partitioned output, manifests, and reproducibility before attempting full order book reconstruction.

## Week 3 Step 2 — First DuckDB query over Parquet

**What was built:**

- A small DuckDB-backed query that reads the partitioned `message_events` Parquet output and returns message type counts.

**Why it matters for data engineering:**

Writing Parquet is only useful if downstream tools can query it. This step proves the output is not just a file on disk; it is usable analytical data.

**Design decisions:**

- The query reads directly from Parquet with DuckDB instead of loading the whole dataset into pandas first.
- The first query is intentionally simple: count rows by `message_type` and `message_class`.
- The CLI returns JSON so it can be used by reports or later demo tooling.

**Tradeoffs:**

- This is not a full analytics layer yet.
- It queries one partition at a time to keep the path explicit and beginner-friendly.

**Questions I should be able to answer:**

- Why use DuckDB after writing Parquet?
- What does grouping by message type prove?
- Why query one partition first instead of scanning all outputs?

**Strong answer in this project context:**

After writing the first `message_events` Parquet dataset, I added a small DuckDB query to prove the data was actually usable. Counting message types is simple, but it verifies the full path from MeatPy messages to Parquet to analytical query results.

## Week 3 Step 3 — Structural validation report

**What was built:**

- A `validate-message-events` command that checks one `message_events` Parquet partition and writes `validation_report.json`.

**Why it matters for data engineering:**

Validation is how a pipeline avoids silently producing bad or incomplete outputs. This first validation layer checks objective structural facts before attempting domain-specific market rules.

**Design decisions:**

- The first rules check file existence, expected columns, positive row count, and manifest row count consistency.
- The report is stored next to the dataset partition it validates.
- Validation is separate from extraction so the run can be inspected step by step.

**Tradeoffs:**

- These checks do not prove order book correctness.
- They are intentionally simple because structural validation is easier to defend than complex market microstructure rules at this stage.

**Questions I should be able to answer:**

- What does structural validation prove?
- What does it not prove?
- Why compare manifest row counts with Parquet row counts?
- Why is validation a separate report instead of just a print statement?

**Strong answer in this project context:**

I started validation with structural checks because they are objective and useful: the Parquet file must exist, have expected columns, contain rows, and agree with the manifest row count. This gives the pipeline an honest quality gate before I attempt more complex ITCH/order-book validation.

## Week 3 Step 4 — Markdown showcase report

**What was built:**

- A Markdown report generator that combines manifest metadata, validation status, Parquet output paths, and DuckDB message type counts into one professor-facing artifact.

**Why it matters for data engineering:**

A pipeline is easier to evaluate when its outputs, checks, and query results are summarized in a clear report. This turns technical artifacts into a demo narrative.

**Design decisions:**

- Build Markdown first because it is simple, versionable, and focused on the pipeline.
- Use the same metrics that a late Week 4 Streamlit app should eventually show.
- Keep the report honest about what is not proven yet.

**Tradeoffs:**

- Markdown is less interactive than Streamlit, but it is faster and less risky at this stage.
- Streamlit is planned for late Week 4 after the report content is stable.

**Questions I should be able to answer:**

- Why create a report before a dashboard?
- What artifacts does the report summarize?
- What would a Streamlit app add later?

**Strong answer in this project context:**

I created a Markdown showcase report first because it lets me present the real pipeline path clearly: Nasdaq ITCH input, MeatPy extraction, Parquet output, manifest, validation report, and DuckDB query. Once that content is stable, Streamlit can make the same story interactive without replacing the engineering work.

## Week 4 Step 1 — Streamlit showcase app

**What was built:**

- A minimal Streamlit app that reads existing pipeline artifacts and displays run metadata, validation status, message type counts, and sample message rows.

**Why it matters for data engineering:**

The app makes the pipeline easier to demo without turning the project into a dashboard-first project. It presents proven artifacts rather than creating new results.

**Design decisions:**

- The app reads `manifest.json`, `validation_report.json`, `message_events` Parquet, and DuckDB-backed message type counts.
- It does not parse raw ITCH files.
- A reusable context loader prepares the data for the app and is covered by tests.

**Tradeoffs:**

- The app is intentionally thin and not highly styled.
- Keeping pipeline logic out of Streamlit makes the project more reproducible and easier to defend.

**Questions I should be able to answer:**

- Why should Streamlit read artifacts instead of raw ITCH data?
- What does the app add beyond the Markdown report?
- How do you keep dashboard code from becoming hidden pipeline logic?

**Strong answer in this project context:**

I kept Streamlit as a thin presentation layer over pipeline artifacts. It reads the manifest, validation report, Parquet output, and DuckDB summaries instead of parsing raw ITCH directly. That keeps the app reproducible and prevents dashboard logic from becoming hidden pipeline logic.

## Week 4 Step 2 â€” Streamlit smoke check and small cleanup

**What was built:**

- No new feature was added.
- The Streamlit app was smoke-tested against existing local artifacts.
- Deprecated `st.dataframe(..., use_container_width=True)` calls were replaced with `width="stretch"`.

**Why it matters for data engineering:**

A professor demo should not depend on hidden manual steps or noisy warnings. This step confirms that the presentation layer can load the real generated artifacts while keeping the pipeline logic in the CLI and reporting modules.

**Design decisions:**

- Use Streamlit's test harness for a quick render check.
- Keep the app as a reader of artifacts, not an executor of extraction or validation.
- Treat warning cleanup as maintenance, not as dashboard expansion.

**Tradeoffs:**

- This does not add a new metric or visualization.
- It improves demo reliability without changing the pipeline's data contract.

**Questions I should be able to answer:**

- What does the Streamlit smoke check prove?
- What does it not prove?
- Why clean up a warning if it does not break the app?

**Strong answer in this project context:**

I smoke-tested Streamlit only to verify that the Week 4 presentation layer can render the existing manifest, validation report, Parquet sample, and DuckDB summary. I also removed a deprecation warning so the demo remains clean, but I did not add new dashboard logic or move pipeline execution into Streamlit.

## Week 5-6 Step 1 â€” Bounded order_events dataset

**What was built:**

- A MeatPy-based `order_events` extraction path that scans a bounded number of ITCH messages and writes order-related events to Parquet.
- The dataset includes add, add-with-MPID, delete, execute, cancel, and replace order-event message classes exposed by MeatPy.
- A manifest records the input file, SHA-256, scan bound, output path, row count, MeatPy probe result, timestamps, and status.

**Why it matters for data engineering:**

This adds a second, more focused data product without pretending to reconstruct the order book. It shows how to derive a usable domain-specific dataset from parsed ITCH messages while keeping the pipeline bounded, reproducible, and inspectable.

**Design decisions:**

- MeatPy still handles message reading.
- Raw ITCH price integers are stored as raw integers; the report does not claim normalized market prices.
- `order_events` is separate from `message_events` so the generic audit trail remains available.
- `AddOrderMPIDMessage` is treated as an add event because MeatPy exposes the same core order fields plus attribution.

**Tradeoffs:**

- This is event-level order data, not a reconstructed book.
- It is richer than `message_events`, but still intentionally bounded by `--max-messages`.

**Strong answer in this project context:**

For Week 6, I added an `order_events` dataset that filters MeatPy message objects into order-event rows. This gives the professor a more substantial output than message counts alone while preserving the same engineering principles: bounded execution, Parquet, manifests, validation, and DuckDB queries.

## Week 5-6 Step 2 â€” Order-event validation and analytics

**What was built:**

- Structural validation for `order_events`.
- DuckDB summaries for event counts, add-side counts, top stocks by add-event count, and activity counts.
- A Week 6 Markdown report that combines `message_events` and `order_events` proof.

**Why it matters for data engineering:**

Validation and analytics prove the new dataset is not just written to disk; it is structurally consistent and queryable.

**Design decisions:**

- Validation checks expected columns, positive row count, manifest consistency, event type presence, expected order references, and increasing sequence numbers.
- DuckDB reads Parquet directly instead of loading the full dataset into dashboard code.
- Streamlit presents Week 6 artifacts only when they already exist.

**Strong answer in this project context:**

I added validation and DuckDB summaries around `order_events` so the Week 6 output is defensible. The current local run scans one million messages, writes 796151 order-event rows, passes 7 structural rules, and produces a Week 6 report without moving pipeline execution into Streamlit.

## Week 5-6 Step 3 - Iris HPC execution proof

**What was completed:**

- A Week 6 SLURM script ran the bounded showcase pipeline on Iris.
- Job `5386100` ran on compute node `iris-111`.
- The HPC run processed the same bounded one million-message scan used for the Week 6 showcase.
- The run wrote `1000000` `message_events` rows and `796151` `order_events` rows.
- Both structural validation reports passed: `message_events` ran 4 rules with 0 failures, and `order_events` ran 7 rules with 0 failures.
- Shareable proof artifacts were copied back into `reports/` and `logs/`, including `reports/week6_showcase_hpc.md`.

**Why it matters for data engineering:**

Running the same bounded pipeline under SLURM proves that the project is not only a laptop demo. The strongest evidence is the combination of a job ID, compute-node log, output row counts, validation reports, and generated report.

**Design decisions:**

- Use SLURM for the heavy run instead of executing on the access node.
- Use a Python 3.11 virtual environment on Iris because the system Python was too old.
- Keep raw Nasdaq data under private scratch storage outside Git.
- Copy back only small proof artifacts, not raw data or Parquet files.

**Strong answer in this project context:**

I ran the bounded Week 6 pipeline on Iris with SLURM job `5386100` on compute node `iris-111`. The run produced one million `message_events` rows, 796151 `order_events` rows, passed all structural validation checks, and generated the copied-back HPC showcase report. That is stronger than a prepared script because it proves the pipeline executed successfully in the target batch environment.
