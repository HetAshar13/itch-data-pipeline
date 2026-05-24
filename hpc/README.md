# HPC Scripts

Do not run heavy code on access/login nodes. Use SLURM from a project checkout on Iris.

## Week 6 Showcase Job

`submit_week6_showcase.slurm` runs the bounded Week 6 pipeline:

- `message_events` extraction and validation
- `order_events` extraction and validation
- DuckDB order-event summary
- `reports/week6_showcase.md`

Example after SSH access and the Python environment are ready on Iris:

```bash
export ITCH_INPUT=/path/to/private/20191230.BX_ITCH_50.gz
export ITCH_DATE=2019-12-30
export OUTPUT_ROOT=outputs/hpc
export MAX_MESSAGES=1000000
export REPORT_PATH=reports/week6_showcase.md

sbatch hpc/submit_week6_showcase.slurm
```

Raw Nasdaq data must stay outside Git. Copy back only generated reports, manifests, validation reports, and small logs needed for the professor demo.
