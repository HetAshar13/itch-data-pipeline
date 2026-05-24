# Decision Log

## Initial decision — Use MeatPy as dependency/baseline

**Decision:** Use MeatPy where appropriate.

**Reason:** MeatPy already handles ITCH parsing/reconstruction/recorders.

**Tradeoff:** Less ownership over low-level ITCH logic, but stronger focus on the data engineering layer.

**Follow-up:** Verify MeatPy API limits during Week 2.

## Data decision — Keep licensed market data outside Git

**Decision:** Real licensed ITCH data may be used later from private/local paths, but it must not be committed to this repo.

**Reason:** Licensed market data usually has redistribution restrictions. Keeping it outside Git makes the repo safer to share while still allowing realistic local experiments.

**Tradeoff:** Tests and examples need public or synthetic fixtures, while full-scale local runs point configs at private input roots.

**Follow-up:** When real data is introduced, document the local path convention without recording private filenames that should not be shared.
