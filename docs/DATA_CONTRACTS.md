# Data Contracts

These contracts define the public meaning of the project datasets. They describe
what each dataset promises, what validation checks prove, and what remains
outside scope. They are intentionally separate from the code so a downstream
reader can understand the data without reading every extractor.

## Shared Rules

- Raw Nasdaq ITCH data stays outside Git, Docker images, CI artifacts, and
  public reports.
- Dataset outputs are partitioned under `outputs/<root>/dataset=<name>/date=<date>/symbol=<symbol>/`.
- Each partition writes `part-000.parquet`, `manifest.json`, and
  `validation_report.json` when validation is run.
- `input_file` records the source path used for the run.
- `input_sha256` records source content identity and is stronger than path
  identity.
- ITCH prices are stored as raw integer price units unless explicitly named
  otherwise. Do not treat raw price fields as normalized dollar prices.
- Validation is structural plus sanity checking. It does not prove complete market microstructure correctness.

## `message_events`

Purpose:

- Broad audit dataset for parsed MeatPy ITCH messages.
- Preserves message-level coverage across many ITCH message classes.
- Useful for row-count proof, message type distribution, and source lineage.

Partition path:

```text
outputs/<root>/dataset=message_events/date=<date>/symbol=ALL/part-000.parquet
```

Schema:

| Column | Meaning |
| --- | --- |
| `sequence_number` | 1-based message position within the bounded scan. |
| `message_type` | MeatPy message type code when present. |
| `message_class` | MeatPy Python message class name. |
| `stock_locate` | ITCH stock locate field when present. |
| `tracking_number` | ITCH tracking number when present. |
| `timestamp_ns` | ITCH timestamp from the message when present. |
| `stock` | Symbol value when the message class exposes one. |
| `description` | MeatPy message description when present. |

Validation guarantees:

- Parquet file exists.
- Expected columns are present.
- Row count is positive.
- Manifest `row_counts.message_events` matches Parquet row count.

Limitations:

- Some fields are nullable because not every ITCH message class exposes every
  attribute.
- This dataset is not an order book and does not reconstruct market state.

## `order_events`

Purpose:

- Focused event-level dataset for order-related MeatPy message objects.
- Captures add, delete, execute, cancel, and replace events.
- Useful for order-event counts, side counts, top add-event symbols, and
  order-reference lineage checks.

Partition path:

```text
outputs/<root>/dataset=order_events/date=<date>/symbol=ALL/part-000.parquet
```

Schema:

| Column | Meaning |
| --- | --- |
| `sequence_number` | 1-based source message position within the bounded scan. |
| `event_type` | Normalized event label: `add`, `delete`, `execute`, `cancel`, or `replace`. |
| `message_type` | MeatPy message type code when present. |
| `message_class` | MeatPy Python message class name. |
| `stock_locate` | ITCH stock locate field when present. |
| `tracking_number` | ITCH tracking number when present. |
| `timestamp_ns` | ITCH timestamp from the message when present. |
| `order_ref` | Order reference for non-replace order events when present. |
| `original_ref` | Original order reference for replace events. |
| `new_ref` | New order reference for replace events. |
| `side` | Buy/sell indicator for add messages when present. |
| `shares` | Shares field when present. |
| `price` | Raw ITCH price integer when present. |
| `canceled_shares` | Canceled shares for cancel events when present. |
| `match_number` | Match number for execution events when present. |
| `stock` | Symbol value when present. |
| `description` | MeatPy message description when present. |

Validation guarantees:

- Parquet file exists.
- Expected columns are present.
- Row count is positive.
- Manifest `row_counts.order_events` matches Parquet row count.
- `event_type` is present for all rows.
- Order reference fields are present according to event type.
- Sequence numbers are monotonically increasing.

Limitations:

- This is still an event dataset, not reconstructed book state.
- Order reference validation proves expected reference fields exist; it does
  not prove all downstream market behavior is correct.
- Raw `price` values are not normalized market prices.

## `lob_snapshots`

Purpose:

- Symbol-specific top-of-book state dataset built through MeatPy LOB
  reconstruction.
- Captures fixed-depth top 5 bid and ask levels after LOB-changing events for
  the requested symbol.
- Useful for spread, two-sided book coverage, and level-1 imbalance summaries.

Partition path:

```text
outputs/<root>/dataset=lob_snapshots/date=<date>/symbol=<symbol>/part-000.parquet
```

Schema:

| Column | Meaning |
| --- | --- |
| `snapshot_number` | 1-based snapshot row number for the target symbol. |
| `sequence_number` | Source ITCH message position that produced the snapshot. |
| `timestamp_ns` | Source message timestamp. |
| `symbol` | Requested symbol for the LOB run. |
| `source_message_type` | MeatPy message type code for the source event. |
| `source_message_class` | MeatPy Python message class for the source event. |
| `bid_price_1_raw`, `bid_price_2_raw`, `bid_price_3_raw`, `bid_price_4_raw`, `bid_price_5_raw` | Raw ITCH bid prices for top 5 levels. |
| `bid_size_1`, `bid_size_2`, `bid_size_3`, `bid_size_4`, `bid_size_5` | Bid sizes for top 5 levels. |
| `ask_price_1_raw`, `ask_price_2_raw`, `ask_price_3_raw`, `ask_price_4_raw`, `ask_price_5_raw` | Raw ITCH ask prices for top 5 levels. |
| `ask_size_1`, `ask_size_2`, `ask_size_3`, `ask_size_4`, `ask_size_5` | Ask sizes for top 5 levels. |
| `spread_1_raw` | `ask_price_1_raw - bid_price_1_raw` when both sides exist. |
| `mid_price_1_raw` | Midpoint of best bid and best ask in raw price units. |
| `level1_imbalance` | `(bid_size_1 - ask_size_1) / (bid_size_1 + ask_size_1)` when both sides exist. |

Validation guarantees:

- Parquet file exists.
- Expected columns are present.
- Row count is positive.
- Manifest `row_counts.lob_snapshots` matches Parquet row count.
- All rows contain only the requested symbol.
- Sequence numbers are monotonically increasing.
- Timestamps do not move backward.
- Top of book is not crossed where both bid and ask exist.

Limitations:

- Only top 5 levels are stored in v1.
- One-sided snapshots are allowed; spread, mid, and imbalance may be null when
  one side is missing.
- Validation checks structure and basic book sanity, not perfect market
  microstructure correctness.
- Raw price fields are not normalized dollar prices.
