# Learning Log

## Session template

**Date:**

**What I worked on:**

**What I understood today:**

**What confused me:**

**What broke:**

**Was it a code bug, data edge case, environment issue, or design issue?**

**What should become a test, validation rule, manifest field, or documentation note?**

**Next small step:**

## Session: 2026-05-02

**What I worked on:**

Set up the local Windows Python environment, installed project requirements, ran tests, and added small infrastructure tests for config loading, hashing, logging, paths, manifests, CLI behavior, and MeatPy probing.

**What I understood today:**

Reliable pipelines need setup and observability pieces before core processing logic. Manifests describe runs, hashes detect file changes, partition paths organize outputs, config files avoid hardcoded settings, logs help trace failures, and CLI commands make checks repeatable.

**What confused me:**

The difference between objects/functions/files, such as `build_sample_manifest()` creating a manifest dictionary, `write_manifest()` writing JSON, and `manifest.json` being an output file.

**What broke:**

PowerShell initially blocked venv activation because script execution was disabled. Running without the venv also caused Python to miss the editable package install.

**Was it a code bug, data edge case, environment issue, or design issue?**

Environment issue.

**What should become a test, validation rule, manifest field, or documentation note?**

The `probe-meatpy` CLI command was added and documented in the README so setup can verify that MeatPy imports before any ITCH processing logic is implemented.

**Next small step:**

Explore the smallest MeatPy sample pipeline experiment, but keep `process_symbol_day()` unchanged until the sample-file path and expected output are understood.

## Session: 2026-05-04

**What I worked on:**

Started the Week 1 MeatPy sample exploration. Downloaded a small public/artificial RITCH fixture and then an official Nasdaq BX ITCH sample into local ignored `data/` storage.

**What I understood today:**

Not every ITCH 5.0-looking file is readable by the exact MeatPy reader version installed. The RITCH fixture is useful public/artificial reference data, but MeatPy 0.4.0's `ITCH50MessageReader` expects a different message framing. The official BX sample file was readable.

**What confused me:**

Why a file documented as ITCH 5.0 could still fail in MeatPy. The issue appears to be file/message framing, not the basic idea of ITCH messages.

**What broke:**

Reading `data_fixtures/ex20101224.TEST_ITCH_50.gz` with MeatPy failed with `ValueError: Empty message data`.

**Was it a code bug, data edge case, environment issue, or design issue?**

Data compatibility issue.

**What should become a test, validation rule, manifest field, or documentation note?**

The first MeatPy-compatible local input is `data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz`, kept outside Git because `data/` and `*.gz` are ignored. The `peek-itch50` CLI command now accepts an input path and reads only a small number of messages first.

**Next small step:**

Use the `peek-itch50` output to decide the smallest manifest-backed sample run, without touching `process_symbol_day()` yet.

## Session: 2026-05-04, continued

**What I worked on:**

Added `sample-peek-run`, the first manifest-backed MeatPy sample command.

**What I understood today:**

A small pipeline run can compose existing helpers: MeatPy reads a few messages, paths decide where outputs go, hashing fingerprints the input, and the manifest records what happened.

**What confused me:**

Why this is not yet the full symbol/day processor. The answer is that this command works at file-level exploration scope and uses `date=unknown` and `symbol=ALL`.

**What broke:**

Nothing during this step. Tests passed and the real command wrote `summary.json` and `manifest.json`.

**Was it a code bug, data edge case, environment issue, or design issue?**

Design step.

**What should become a test, validation rule, manifest field, or documentation note?**

The manifest-backed run now records the input SHA-256, message count, output summary path, MeatPy probe result, and validation status as `not_run`.

**Next small step:**

Review the generated `summary.json` and `manifest.json`, then decide what extra manifest fields are actually useful before implementing any symbol/day processing.

## Session: 2026-05-19

**What I worked on:**

Preserved the post-compression project state after completing the Week 12 final
`SPY` until-EOF Iris proof and before starting Week 13 reproducibility work.

**What I understood today:**

Docker is a portable runtime environment for Python, dependencies, package
installation, tests, and CLI smoke checks. It does not replace Iris HPC and
must not include raw Nasdaq data. Before making the project easier to run in
CI or Docker, the repo should first prove that raw proprietary data and large
generated outputs are not accidentally included.

**What confused me:**

Which files a raw-data safety check should reject versus allow.

**What broke:**

Nothing in the pipeline. The issue was preserving direction before context
compression.

**Was it a code bug, data edge case, environment issue, or design issue?**

Design and governance issue.

**What should become a test, validation rule, manifest field, or documentation note?**

Add a raw-data safety check that rejects raw ITCH files and large generated
Parquet outputs while allowing small proof artifacts such as copied JSON,
SLURM logs, reports, and known proof bundles.

**Next small step:**

Add the smallest tested raw-data safety scanner/CLI command before wiring it
into CI or adding Docker.
