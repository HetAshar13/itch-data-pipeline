# Week 11 LOB Multi-Symbol Comparison

## Scope

This report compares the first bounded multi-symbol Iris LOB snapshot run.

All symbols used the same pipeline recipe:

- Dataset: `lob_snapshots`
- Date: `2019-12-30`
- Input file: private Nasdaq BX ITCH file on Iris scratch storage
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Message scan bound: `2000000`
- Snapshot depth: top 5 bid/ask levels
- SLURM script: `hpc/submit_lob_snapshots.slurm`
- Validation rules per symbol: `8`

The comparison is based on copied JSON proof artifacts under
`logs/week11_lob_2m/`. No raw Nasdaq data or large Parquet outputs were copied
into the repo.

## Results

| Symbol | Job ID | Snapshots | Validation | Rules Failed | Two-Sided Snapshots | Two-Sided % | Median Spread Raw | Avg Spread Raw | Avg L1 Imbalance |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY | `5404108` | `59163` | passed | `0` | `59104` | `99.9002755100316` | `300.0` | `351.1166756903086` | `-0.036631156986337975` |
| QQQ | `5404160` | `43958` | passed | `0` | `43107` | `98.06406114927886` | `300.0` | `348.1847495766349` | `-0.021973774924295565` |
| IWM | `5404169` | `29096` | passed | `0` | `28322` | `97.33984052790761` | `300.0` | `360.2076124567474` | `0.153155043458018` |

## Interpretation

All three symbols passed the same structural and sanity validation checks. This
shows that the MeatPy-based LOB snapshot pipeline works across multiple active
ETF symbols, not only the original `SPY` smoke target.

`SPY` produced the most snapshots in the bounded scan, followed by `QQQ`, then
`IWM`. All three symbols had high two-sided snapshot percentages, which means
most emitted snapshots had both a best bid and best ask. That makes spread and
level-1 imbalance summaries meaningful for this bounded comparison.

The median raw spread was `300.0` for all three symbols. Average raw spread was
similar across the three runs, with `QQQ` slightly lower and `IWM` slightly
higher in this bounded sample. The level-1 imbalance averages differ by symbol:
`SPY` and `QQQ` were slightly negative, while `IWM` was positive.

## Limitations

- This is a bounded run over the first `2000000` messages, not a full-day result.
- Prices are raw ITCH integer units; this report does not claim normalized market prices.
- Validation is structural plus sanity checking, not proof of full market microstructure correctness.
- `SPY` came from the Week 10 output root, while `QQQ` and `IWM` came from the Week 11 output root; the comparison uses copied proof artifacts to keep the local repo small.
- Large Parquet outputs remain on private Iris scratch storage.

## Next Scale Step

The next controlled scale-up should increase one variable at a time. A reasonable
next run is `SPY` at `10000000` messages using the same SLURM script and proof
artifact pattern. If that passes, the same larger bound can be repeated for
`QQQ` and `IWM`.

