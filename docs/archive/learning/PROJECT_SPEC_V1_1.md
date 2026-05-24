# Project Spec v1.1

## Title

HPC Market Data Engineering Pipeline for Reliable ITCH Processing

## Classification

This is a **data engineering integration and data product project**, not a novel research contribution.

## Core objective

Use existing ITCH tooling such as MeatPy for parsing/reconstruction where appropriate, then build the engineering layer around it:

- batch execution
- partitioned Parquet outputs
- run manifests
- deterministic reruns
- structural validation
- DuckDB analytics views later

## Current starter scope

This repo targets **Week 1-2 only**:

- local Windows setup
- learning contract
- manifest/hash/logging infrastructure
- MeatPy sample-file exploration
- no full validation engine yet
- no dashboard yet
- no dbt, Spark, Airflow, Dagster, or Prefect

## Out of scope for MVP

- custom ITCH parser rewrite
- stock prediction
- ML anomaly detection
- complex dashboard
- options data
- Spark
- Airflow
- Dagster
- Snowflake
