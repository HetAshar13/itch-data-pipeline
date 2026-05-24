#!/bin/bash
#SBATCH --job-name=itch_symbol_day
#SBATCH --output=logs/hpc/%x_%j.out
#SBATCH --error=logs/hpc/%x_%j.err
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G

echo "Job started on $(hostname)"
echo "SLURM_JOB_ID=$SLURM_JOB_ID"
echo "DATE=$ITCH_DATE"
echo "SYMBOL=$ITCH_SYMBOL"

# Future command:
# python -m itch_data_pipeline.runner.process_symbol_day --date "$ITCH_DATE" --symbol "$ITCH_SYMBOL"

echo "Job finished"
