#!/bin/bash

#SBATCH --job-name=lammps-doe
#SBATCH --array=1-300
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=logs/lammps_%A_%a.out
#SBATCH --error=logs/lammps_%A_%a.err

echo "========================================"
echo "LAMMPS HPC JOB"
echo "========================================"

echo "Job ID: $SLURM_JOB_ID"
echo "Array ID: $SLURM_ARRAY_TASK_ID"

# -------------------------------------------------
# Create required directories
# -------------------------------------------------

mkdir -p logs
mkdir -p simulations

# -------------------------------------------------
# Read parameter corresponding to this job
# -------------------------------------------------

PARAMETER_FILE="results/doe_300_points.csv"

LINE=$((SLURM_ARRAY_TASK_ID + 1))

PARAMETERS=$(sed -n "${LINE}p" "$PARAMETER_FILE")

echo "Parameters:"
echo "$PARAMETERS"

# -------------------------------------------------
# Extract temperature and deformation
# -------------------------------------------------

TEMPERATURE=$(echo "$PARAMETERS" | cut -d',' -f2)
DEFORMATION=$(echo "$PARAMETERS" | cut -d',' -f3)

echo "Temperature: $TEMPERATURE"
echo "Deformation: $DEFORMATION"

# -------------------------------------------------
# Create simulation directory
# -------------------------------------------------

RUN_DIR="simulations/run_${SLURM_ARRAY_TASK_ID}"

mkdir -p "$RUN_DIR"

# -------------------------------------------------
# Copy LAMMPS input files
# -------------------------------------------------

cp -r ../lammps_example/* "$RUN_DIR/"

cd "$RUN_DIR"

# -------------------------------------------------
# Modify simulation parameters
# -------------------------------------------------

sed -i \
"s/variable temp equal .*/variable temp equal $TEMPERATURE/" \
init.mod

sed -i \
"s/variable up equal .*/variable up equal $DEFORMATION/" \
init.mod

# -------------------------------------------------
# Run LAMMPS
# -------------------------------------------------

lmp -in in.elastic

echo "========================================"
echo "JOB COMPLETED"
echo "========================================"