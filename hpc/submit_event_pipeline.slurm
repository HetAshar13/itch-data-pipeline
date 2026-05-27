#!/bin/bash
#SBATCH --job-name=itch_event_pipeline
#SBATCH --output=logs/hpc/%x_%j.out
#SBATCH --error=logs/hpc/%x_%j.err
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G

set -euo pipefail

: "${ITCH_INPUT:?Set ITCH_INPUT to a private MeatPy-readable ITCH 5.0 file path on Iris.}"
ITCH_DATE="${ITCH_DATE:-2019-12-30}"
OUTPUT_ROOT="${OUTPUT_ROOT:-outputs/hpc}"
MAX_MESSAGES="${MAX_MESSAGES:-1000000}"
REPORT_PATH="${REPORT_PATH:-reports/event_pipeline_showcase.md}"

mkdir -p logs/hpc reports

echo "Job started on $(hostname)"
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unknown}"
echo "ITCH_INPUT=$ITCH_INPUT"
echo "ITCH_DATE=$ITCH_DATE"
echo "OUTPUT_ROOT=$OUTPUT_ROOT"
echo "MAX_MESSAGES=$MAX_MESSAGES"
echo "REPORT_PATH=$REPORT_PATH"

python -m itch_data_pipeline.cli healthcheck
python -m itch_data_pipeline.cli probe-meatpy

python -m itch_data_pipeline.cli extract-itch50-sample \
  --input "$ITCH_INPUT" \
  --date "$ITCH_DATE" \
  --max-messages "$MAX_MESSAGES" \
  --output-root "$OUTPUT_ROOT"

python -m itch_data_pipeline.cli validate-message-events \
  --output-root "$OUTPUT_ROOT" \
  --date "$ITCH_DATE"

python -m itch_data_pipeline.cli extract-order-events-sample \
  --input "$ITCH_INPUT" \
  --date "$ITCH_DATE" \
  --max-messages "$MAX_MESSAGES" \
  --output-root "$OUTPUT_ROOT"

python -m itch_data_pipeline.cli validate-order-events \
  --output-root "$OUTPUT_ROOT" \
  --date "$ITCH_DATE"

python -m itch_data_pipeline.cli query-order-event-summary \
  --output-root "$OUTPUT_ROOT" \
  --date "$ITCH_DATE" \
  --limit 10

python -m itch_data_pipeline.cli write-event-pipeline-report \
  --output-root "$OUTPUT_ROOT" \
  --date "$ITCH_DATE" \
  --report-path "$REPORT_PATH" \
  --top-n 10

echo "Job finished"
