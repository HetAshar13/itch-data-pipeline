# Week 11 HPC LOB 10M Scale Status

## Current Status

The larger bounded Iris LOB comparison succeeded for:

- `SPY`
- `QQQ`
- `IWM`

Each symbol used a `10000000` message scan bound.

## Controlled Run Setup

All three runs used:

- Dataset: `lob_snapshots`
- Date: `2019-12-30`
- Input file: `/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz`
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Output root: `/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_scale10m`
- Message scan bound: `10000000`
- Snapshot depth: `5`
- SLURM script: `hpc/submit_lob_snapshots.slurm`
- Compute node: `iris-111`
- Validation rules per symbol: `8`

## Results

| Symbol | Job ID | Snapshots | Validation | Rules Failed | Two-Sided % | Median Spread Raw | Avg Spread Raw | Avg L1 Imbalance | Duration Seconds |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY | `5404209` | `206927` | passed | `0` | `99.9714875294186` | `300.0` | `325.67240945917206` | `0.013739799889758` | `553.374562` |
| QQQ | `5404299` | `172052` | passed | `0` | `99.5053820937856` | `300.0` | `362.34075735538926` | `0.006743096011588524` | `174.753771` |
| IWM | `5404485` | `156647` | passed | `0` | `99.50589542091454` | `300.0` | `288.22502935081764` | `0.13574819077244718` | `144.960816` |

## Local Proof Artifacts

Small proof artifacts were copied back locally under:

```text
logs/week11_lob_10m/
```

The copied archive is:

```text
logs/week11_lob_10m.tar.gz
```

For each symbol, the proof directory contains:

- SLURM `.out`
- SLURM `.err`
- manifest JSON
- validation JSON
- DuckDB summary JSON

No raw Nasdaq data or large Parquet files were copied into the repo.

## Learning Takeaway

The `2M` run proved the multi-symbol path at a moderate bound. The `10M` run
tested scale while keeping the same symbols, input file, script, schema, and
validation rules. Since all three `10M` runs passed, the project now has stronger
HPC evidence that the MeatPy-based LOB snapshot pipeline scales beyond a smoke
run.

