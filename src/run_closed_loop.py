import csv
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
PARAMETERS = ROOT / "inputs" / "parameters.json"
EXPERIMENTS = ROOT / "inputs" / "experimental_data.csv"
STATE = ROOT / "results" / "closed_loop_state.csv"
HISTORY = ROOT / "results" / "closed_loop_history.csv"
COMPARISON = ROOT / "results" / "simulation_experiment_comparison.csv"

def run(name):
    print("\n" + "=" * 60)
    print("RUNNING:", name)
    print("=" * 60)
    r = subprocess.run([str(PYTHON), str(ROOT / "src" / name)], cwd=ROOT)
    if r.returncode:
        raise SystemExit(f"{name} failed with code {r.returncode}")

with PARAMETERS.open() as fh:
    p = json.load(fh)

run("generate_inputs.py")
run("run_simulation.py")
run("analyze_results.py")

# Visualization is deliberately run with the OVITO environment.
ovito_python = ROOT / "ovito-env" / "Scripts" / "python.exe"
visualize = ROOT / "src" / "Visualize.py"
if ovito_python.exists() and visualize.exists():
    print("\nRunning OVITO visualization...")
    r = subprocess.run([str(ovito_python), str(visualize)], cwd=ROOT)
    if r.returncode:
        print("WARNING: OVITO visualization failed; simulation pipeline remains valid.")

# Compare if measurements exist.
run("compare_experiment.py")

status = "WAITING_FOR_EXPERIMENT"
if COMPARISON.exists():
    rows = list(csv.DictReader(COMPARISON.open()))
    if rows and rows[0].get("status") != "WAITING_FOR_EXPERIMENT":
        status = "COMPARISON_COMPLETE" if rows else "EXPERIMENT_AVAILABLE_BUT_NO_MATCHING_CURRENT_POINT"

ROOT.joinpath("results").mkdir(exist_ok=True)
timestamp = datetime.now().isoformat()

write_header = not HISTORY.exists()
with HISTORY.open("a", newline="") as fh:
    w = csv.writer(fh)
    if write_header:
        w.writerow(["timestamp", "temperature", "deformation", "status"])
    w.writerow([timestamp, p["temperature"], p.get("deformation", 0.02), status])

with STATE.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["timestamp", "temperature", "deformation", "status"])
    w.writerow([timestamp, p["temperature"], p.get("deformation", 0.02), status])

print("\n" + "=" * 60)
print("CLOSED LOOP STATUS:", status)
print("=" * 60)
