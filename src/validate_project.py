from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

checks = {
    "parameters": ROOT / "inputs" / "parameters.json",
    "experimental_template": ROOT / "inputs" / "experimental_data.csv",
    "simulation_properties": ROOT / "results" / "properties.csv",
    "DOE_12": ROOT / "results" / "doe_dataset.csv",
    "DOE_300": ROOT / "results" / "doe_300_points.csv",
    "ML_results": ROOT / "results" / "ml_results.csv",
    "expert_feedback": ROOT / "results" / "expert_feedback.csv",
    "HPC_script": ROOT / "HPC" / "project" / "run_lammps_array.slurm",
    "HPC_collector": ROOT / "src" / "collect_hpc_results.py",
    "multiscale": ROOT / "results" / "multiscale_material_properties.csv",
}

for name, path in checks.items():
    print(f"{'[OK]' if path.exists() else '[MISSING]':10} {name}: {path}")

print("\nValidation complete.")
