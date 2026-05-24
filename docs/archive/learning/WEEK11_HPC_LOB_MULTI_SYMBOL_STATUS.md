# Week 11 HPC LOB Multi-Symbol Status

## Current Status

The first bounded multi-symbol Iris LOB run succeeded for:

- `SPY`
- `QQQ`
- `IWM`

All runs used the same reusable SLURM script:

```text
hpc/submit_lob_snapshots.slurm
```

The controlled variables were:

- date: `2019-12-30`
- input file: `/scratch/users/hashar/itch-data-pipeline/data/nasdaq_bx_itch/20191230.BX_ITCH_50.gz`
- message scan bound: `2000000`
- output root: `/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_week11` for `QQQ` and `IWM`
- validation rules: same `8` `lob_snapshots` rules for every symbol

`SPY` used the Week 10 output root and is included as the baseline symbol for
comparison.

## Results

| Symbol | Job ID | Node | Snapshots | Validation | Rules Failed | Two-Sided % | Median Spread Raw | Avg Spread Raw | Avg L1 Imbalance |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| SPY | `5404108` | `iris-111` | `59163` | passed | `0` | `99.9002755100316` | `300.0` | `351.1166756903086` | `-0.036631156986337975` |
| QQQ | `5404160` | unknown from copied proof | `43958` | passed | `0` | `98.06406114927886` | `300.0` | `348.1847495766349` | `-0.021973774924295565` |
| IWM | `5404169` | unknown from copied proof | `29096` | passed | `0` | `97.33984052790761` | `300.0` | `360.2076124567474` | `0.153155043458018` |

## Local Proof Artifacts

Small proof artifacts were copied back locally under:

```text
logs/week11_lob_2m/
```

The copied archive is:

```text
logs/week11_lob_2m.tar.gz
```

For each symbol, the proof directory contains:

- SLURM `.out`
- SLURM `.err`
- manifest JSON
- validation JSON
- DuckDB summary JSON

No raw Nasdaq data or large Parquet files were copied into the repo.

## Learning Takeaway

This is stronger than a single-symbol run because the same pipeline recipe was
used across multiple high-activity ETF symbols. Holding the date, input file,
message bound, script, and validation rules constant makes the symbol the main
variable. That makes differences in snapshot count, two-sided percentage,
spread, and imbalance easier to interpret.

