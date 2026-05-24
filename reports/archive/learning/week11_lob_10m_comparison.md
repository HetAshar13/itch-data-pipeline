# Week 11 LOB 10M Multi-Symbol Comparison

## Scope

This report compares the larger bounded Iris LOB snapshot run for `SPY`, `QQQ`,
and `IWM`.

All symbols used the same pipeline recipe:

- Dataset: `lob_snapshots`
- Date: `2019-12-30`
- Input file: private Nasdaq BX ITCH file on Iris scratch storage
- Input SHA-256: `b7a56dafeaa8300308e24828b21f5595909b0fff3b5182b5c2f160917f76302f`
- Message scan bound: `10000000`
- Snapshot depth: top 5 bid/ask levels
- SLURM script: `hpc/submit_lob_snapshots.slurm`
- Compute node: `iris-111`
- Validation rules per symbol: `8`

The comparison is based on copied JSON proof artifacts. No raw Nasdaq data or
large Parquet outputs were copied into the public repo.

## Results

| Symbol | Job ID | Snapshots | Validation | Rules Failed | Two-Sided Snapshots | Two-Sided % | Median Spread Raw | Avg Spread Raw | Avg L1 Imbalance | Duration Seconds |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SPY | `5404209` | `206927` | passed | `0` | `206868` | `99.9714875294186` | `300.0` | `325.67240945917206` | `0.013739799889758` | `553.374562` |
| QQQ | `5404299` | `172052` | passed | `0` | `171201` | `99.5053820937856` | `300.0` | `362.34075735538926` | `0.006743096011588524` | `174.753771` |
| IWM | `5404485` | `156647` | passed | `0` | `155873` | `99.50589542091454` | `300.0` | `288.22502935081764` | `0.13574819077244718` | `144.960816` |

## Interpretation

All three symbols passed validation at the larger `10000000` message bound. This
is stronger than the earlier `2000000` message comparison because it tests the
same pipeline at a larger scan size while keeping the run recipe stable.

`SPY` produced the most snapshots, followed by `QQQ`, then `IWM`. All three
symbols had more than `99.5%` two-sided snapshots, so spread and level-1
imbalance remain meaningful for this bounded comparison.

The median raw spread stayed at `300.0` for all three symbols. Average raw spread
varied by symbol, with `IWM` lower in this `10M` run and `QQQ` higher. The
average level-1 imbalance was positive for all three symbols in this larger
bounded sample.

## 2M To 10M Scale Check

| Symbol | 2M Snapshots | 10M Snapshots | Increase |
| --- | ---: | ---: | ---: |
| SPY | `59163` | `206927` | `147764` |
| QQQ | `43958` | `172052` | `128094` |
| IWM | `29096` | `156647` | `127551` |

Snapshot count increased for all symbols, but not exactly linearly. That is
expected because emitted snapshots depend on how many target-symbol book-changing
events appear in the scanned ITCH message range, not only on the raw scan bound.

## Limitations

- This is still a bounded scan, not a full-day result.
- Prices are raw ITCH integer units; this report does not claim normalized market prices.
- Validation is structural plus sanity checking, not proof of full market microstructure correctness.
- Large Parquet outputs remain on private Iris scratch storage.
- Runtime comparisons are approximate because cluster load and scheduling context can vary.
