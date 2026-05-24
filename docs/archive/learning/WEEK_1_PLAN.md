# Week 1 Plan

## Goal

Understand the project, prepare your local environment, and run basic infrastructure tests.

## Day 1: Read and explain

Read:
- `README.md`
- `LEARNING_FIRST_RULES.md`
- `docs/PROJECT_SPEC_V1_1.md`
- `docs/HPC_ACCESS_CHECKLIST.md`

Then write a short note in `docs/LEARNING_LOG.md`:
1. What does MeatPy already do?
2. What does this project add?
3. Why are run manifests useful?
4. Why do we avoid rebuilding the parser?

## Day 2: Local setup

Run the setup commands in the README.

## Day 3: Understand manifests

Open:
- `src/itch_data_pipeline/manifests/manifest_writer.py`
- `tests/test_manifests.py`

Run:
```powershell
pytest tests/test_manifests.py
python -m itch_data_pipeline.cli write-sample-manifest
```

## Day 4: Understand hashing and deterministic reruns

Open:
- `src/itch_data_pipeline/utils/hashing.py`
- `tests/test_hashing.py`
- `tests/test_rerun_determinism.py`

## Day 5: MeatPy exploration

Ask your coding assistant to help you:
1. verify MeatPy installation
2. locate MeatPy docs/examples
3. identify a public sample ITCH file
4. plan the first MeatPy sample-file processing step

## Week 1 success criteria

- tests pass
- healthcheck runs
- you can explain the project in your own words
- you understand manifest and hashing utilities
