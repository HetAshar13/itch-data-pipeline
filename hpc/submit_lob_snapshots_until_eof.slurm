#!/bin/bash
#SBATCH --job-name=itch_lob_until_eof
#SBATCH --output=logs/hpc/%x_%j.out
#SBATCH --error=logs/hpc/%x_%j.err
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=12G

set -euo pipefail

: "${ITCH_INPUT:?Set ITCH_INPUT to a private MeatPy-readable ITCH 5.0 file path on Iris.}"
ITCH_DATE="${ITCH_DATE:-2019-12-30}"
SYMBOL="${SYMBOL:-SPY}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/scratch/users/hashar/itch-data-pipeline/outputs/hpc_lob_until_eof}"
SUMMARY_PATH="${SUMMARY_PATH:-/scratch/users/hashar/itch-data-pipeline/reports/lob_summary_${SYMBOL}_${ITCH_DATE}_until_eof.json}"

mkdir -p logs/hpc "$(dirname "$SUMMARY_PATH")"

echo "Job started on $(hostname)"
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unknown}"
echo "RUN_MODE=until_eof"
echo "ITCH_INPUT=$ITCH_INPUT"
echo "ITCH_DATE=$ITCH_DATE"
echo "SYMBOL=$SYMBOL"
echo "OUTPUT_ROOT=$OUTPUT_ROOT"
echo "SUMMARY_PATH=$SUMMARY_PATH"

python -m itch_data_pipeline.cli healthcheck
python -m itch_data_pipeline.cli probe-meatpy

python -m itch_data_pipeline.cli extract-lob-snapshots-sample \
  --input "$ITCH_INPUT" \
  --date "$ITCH_DATE" \
  --symbol "$SYMBOL" \
  --until-eof \
  --output-root "$OUTPUT_ROOT"

python -m itch_data_pipeline.cli validate-lob-snapshots \
  --output-root "$OUTPUT_ROOT" \
  --date "$ITCH_DATE" \
  --symbol "$SYMBOL"

python -m itch_data_pipeline.cli query-lob-summary \
  --output-root "$OUTPUT_ROOT" \
  --date "$ITCH_DATE" \
  --symbol "$SYMBOL" | tee "$SUMMARY_PATH"

echo "Job finished"
