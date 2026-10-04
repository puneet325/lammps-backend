#!/bin/bash

#SBATCH --job-name=silicon-doe
#SBATCH --array=1-300
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=logs/job_%A_%a.out
#SBATCH --error=logs/job_%A_%a.err

set -euo pipefail

echo "=========================================="
echo "LAMMPS DOE JOB"
echo "=========================================="

echo "Job ID       : $SLURM_JOB_ID"
echo "Array ID     : $SLURM_ARRAY_TASK_ID"

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

PARAMETER_FILE="results/doe_300_points.csv"

# The CSV has a header, so array job 1 reads line 2.
LINE=$((SLURM_ARRAY_TASK_ID + 1))

PARAMETERS=$(sed -n "${LINE}p" "$PARAMETER_FILE")

RUN_ID=$(echo "$PARAMETERS" | cut -d',' -f1)
TEMPERATURE=$(echo "$PARAMETERS" | cut -d',' -f2)
DEFORMATION=$(echo "$PARAMETERS" | cut -d',' -f3)

echo "Run ID       : $RUN_ID"
echo "Temperature  : $TEMPERATURE"
echo "Deformation  : $DEFORMATION"

RUN_DIR="simulations/run_${SLURM_ARRAY_TASK_ID}"

rm -rf "$RUN_DIR"
mkdir -p "$RUN_DIR"

cp -r lammps_examples/* "$RUN_DIR/"

cd "$RUN_DIR"

echo "Patching temperature..."

sed -i \
"s/variable temp equal .*/variable temp equal $TEMPERATURE/" \
init.mod

echo "Patching deformation..."

sed -i \
"s/variable up equal .*/variable up equal $DEFORMATION/" \
init.mod

echo "Checking parameters..."

grep "variable temp equal" init.mod
grep "variable up equal" init.mod

echo "Running LAMMPS..."

lmp -in in.elastic

echo "LAMMPS completed."

echo "=========================================="
echo "JOB FINISHED"
echo "Run ID      : $RUN_ID"
echo "Temperature : $TEMPERATURE"
echo "Deformation : $DEFORMATION"
echo "=========================================="