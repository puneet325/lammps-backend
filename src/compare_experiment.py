import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "inputs" / "parameters.json"
EXPERIMENTS = ROOT / "inputs" / "experimental_data.csv"
DOE = ROOT / "results" / "doe_dataset.csv"
PROPERTIES = ROOT / "results" / "properties.csv"
RESULT = ROOT / "results" / "simulation_experiment_comparison.csv"

def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def load_properties():
    data = {}
    with PROPERTIES.open() as fh:
        for row in csv.DictReader(fh):
            data[row["Property"]] = f(row["Value"])
    return data

with PARAMETERS.open() as fh:
    p = json.load(fh)

temperature = float(p["temperature"])
deformation = float(p.get("deformation", 0.02))

rows = list(csv.DictReader(EXPERIMENTS.open()))
valid = []
for r in rows:
    if f(r.get("experimental_Bulk_Modulus")) is not None:
        valid.append(r)

RESULT.parent.mkdir(parents=True, exist_ok=True)

if not valid:
    with RESULT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["status", "message"])
        w.writerow(["WAITING_FOR_EXPERIMENT", "No experimental Bulk Modulus measurements supplied."])
    print("STATUS: WAITING_FOR_EXPERIMENT")
    print("No real experimental measurements are available.")
    raise SystemExit(0)

# Prefer an exact current-parameter match in the DOE dataset.
sim = None
if DOE.exists():
    for r in csv.DictReader(DOE.open()):
        if abs(f(r["temperature"]) - temperature) < 1e-9 and abs(f(r["deformation"]) - deformation) < 1e-9:
            sim = r
            break

if sim is None:
    props = load_properties()
    sim = {
        "temperature": temperature,
        "deformation": deformation,
        "Bulk_Modulus": props.get("Bulk Modulus"),
        "C11": props.get("C11"),
        "Poisson_Ratio": props.get("Poisson Ratio"),
    }

out_rows = []
for exp in valid:
    if abs(f(exp["temperature"]) - temperature) < 1e-9 and abs(f(exp["deformation"]) - deformation) < 1e-9:
        pairs = [
            ("C11", sim.get("C11"), exp.get("experimental_C11")),
            ("Bulk_Modulus", sim.get("Bulk_Modulus"), exp.get("experimental_Bulk_Modulus")),
            ("Poisson_Ratio", sim.get("Poisson_Ratio"), exp.get("experimental_Poisson_Ratio")),
        ]
        for prop, s, e in pairs:
            s, e = f(s), f(e)
            if s is not None and e is not None:
                abs_err = abs(s - e)
                pct = abs_err / abs(e) * 100 if e != 0 else None
                out_rows.append([temperature, deformation, prop, s, e, abs_err, pct])

with RESULT.open("w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["temperature", "deformation", "property", "simulation", "experiment", "absolute_error", "percent_error"])
    w.writerows(out_rows)

if not out_rows:
    print("STATUS: EXPERIMENT_AVAILABLE_BUT_NO_MATCHING_CURRENT_POINT")
else:
    print("STATUS: COMPARISON_COMPLETE")
    for r in out_rows:
        print(f"{r[2]}: simulation={r[3]:.6f}, experiment={r[4]:.6f}, error={r[6]:.3f}%")
