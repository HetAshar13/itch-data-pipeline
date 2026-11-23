# LiquidityIQ Case Study

In the bundled QQQ snapshot, a 50,000-share buy fills an estimated 42,500
shares across the five displayed ask levels at a weighted average of $213.44.
The remaining 7,500 shares have no visible price in that snapshot. For the
inputs and result, see the [demo fixture](../data_fixtures/liquidityiq_demo.json)
and [Execution Cost Lab](linkedin_assets/liquidityiq_execution_cost_lab.png).

## Pre-trade use

A single best ask gives a buyer a price and the quantity available at that
price. LiquidityIQ walks the displayed ask levels to estimate how much of
an order can fill, its weighted average price and the cost relative to
the midpoint. A desk can compare proposed order sizes or time windows
using displayed liquidity. The estimates use one visible book snapshot
at a time and leave out market impact, queue position and hidden liquidity.

The underlying event and book datasets also support comparisons of spreads,
depth and cancellation activity. Input hashes, run manifests and validation
reports document how the licensed feed was processed and can be shared
independently of the feed.

## Product Design

LiquidityIQ has two modes:

- `demo`: loads tracked aggregate JSON data with no raw ITCH, no Parquet, and no
  order-level records.
- `local_artifacts`: reads private generated `lob_snapshots` and `order_events`
  artifacts when available.

The app is read-only. It does not parse raw ITCH, run MeatPy extraction, submit
SLURM jobs, or mutate output datasets.

## Analytics Mart

The mart grain is one row per symbol, date, and 1-minute bucket. It derives:

- spread in raw ITCH units and normalized display units,
- top-5 bid depth, ask depth, and combined visible depth,
- level-1 imbalance,
- two-sided snapshot coverage,
- event count and add/cancel/delete/replace/execute counts,
- cancel-to-add and execute-to-add ratios,
- liquidity score,
- stress regime label.

Raw source prices remain unchanged. Display prices are separate derived fields
using an explicit `10,000` scale.

## Execution Cost Lab

The simulator estimates deterministic cost against visible top-5 book depth.

For a buy order, it consumes ask levels from best ask outward. For a sell order,
it consumes bid levels from best bid outward. It returns visible depth,
estimated fillable quantity, weighted average execution price, midpoint,
slippage versus mid, spread cost in basis points, depth consumed percentage,
insufficient-liquidity warnings, and a low/medium/high risk label.

This is not a full transaction-cost-analysis model. It does not estimate hidden
liquidity, queue position, latency, market impact, venue fees, or future price
movement. It is a transparent visible-book diagnostic.

## How The Pipeline Powers The Product

LiquidityIQ exists because the lower layers already provide trusted artifacts:

1. MeatPy parses ITCH and reconstructs LOB state.
2. Pipeline runners write partitioned Parquet datasets.
3. Manifests record lineage and input hashes.
4. Validation checks structure, row counts, ordering, symbols, and crossed-book
   sanity.
5. DuckDB and pandas derive aggregate liquidity bars.
6. Streamlit presents the results without touching raw data.

## Evidence

The public repo includes proof that the upstream pipeline processed real Iris
HPC workloads:

- `29,156,757` SPY messages scanned until EOF.
- `614,578` SPY LOB snapshots.
- `535,626` 10M multi-symbol LOB snapshots across SPY, QQQ, and IWM.
- `1,000,000` message-event rows.
- `796,151` order-event rows.
- `138` local tests.

## Limitations

- Demo mode uses aggregate public-safe data only.
- Visible-book cost uses top-5 displayed depth only.
- Liquidity score is deterministic and explainable, not ML.
- Validation proves structural consistency and sanity, not complete exchange
  correctness.
- Raw Nasdaq data and generated Parquet outputs remain private.
