from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

DOE_FILE = ROOT / "results" / "doe_300_points.csv"
EXPERIMENT_FILE = ROOT / "inputs" / "experimental_data.csv"

OUTPUT_FILE = ROOT / "results" / "next_simulation_parameters.csv"


print("=" * 60)
print("NEXT SIMULATION PARAMETER SELECTOR")
print("=" * 60)


# ---------------------------------------------------------
# 1. Load files
# ---------------------------------------------------------

if not DOE_FILE.exists():
    print("ERROR: 300-point DoE file not found.")
    raise SystemExit(1)

if not EXPERIMENT_FILE.exists():
    print("ERROR: experimental data file not found.")
    raise SystemExit(1)


doe = pd.read_csv(DOE_FILE)
experimental = pd.read_csv(EXPERIMENT_FILE)

print(f"Total candidate points: {len(doe)}")


# ---------------------------------------------------------
# 2. Check experimental measurements
# ---------------------------------------------------------

experimental_columns = [
    "experimental_C11",
    "experimental_Bulk_Modulus",
    "experimental_Poisson_Ratio"
]

has_data = experimental[experimental_columns].notna().any().any()


if not has_data:

    print()
    print("No real experimental measurements are available.")
    print()
    print("STATUS: WAITING_FOR_EXPERIMENT")
    print()
    print("No new simulation parameters selected.")

    output = pd.DataFrame([{
        "status": "WAITING_FOR_EXPERIMENT",
        "temperature": "",
        "deformation": "",
        "reason": "Real experimental measurements are required."
    }])

    output.to_csv(OUTPUT_FILE, index=False)

    print(f"Output saved to: {OUTPUT_FILE}")

    raise SystemExit(0)


# ---------------------------------------------------------
# 3. Find experimental points that have Bulk Modulus
# ---------------------------------------------------------

experimental_valid = experimental.dropna(
    subset=["experimental_Bulk_Modulus"]
).copy()


if len(experimental_valid) == 0:

    print()
    print("No experimental Bulk Modulus measurements found.")
    print("STATUS: WAITING_FOR_EXPERIMENT")

    output = pd.DataFrame([{
        "status": "WAITING_FOR_EXPERIMENT",
        "temperature": "",
        "deformation": "",
        "reason": "Bulk Modulus measurements are required."
    }])

    output.to_csv(OUTPUT_FILE, index=False)

    raise SystemExit(0)


# ---------------------------------------------------------
# 4. Merge experiment with available simulation results
# ---------------------------------------------------------

simulation_file = ROOT / "results" / "hpc_300_results.csv"

if not simulation_file.exists():

    print()
    print("HPC simulation result file not found.")
    print()
    print("The optimizer needs completed simulation results")
    print("before it can calculate simulation/experiment error.")
    print()
    print("STATUS: WAITING_FOR_HPC_RESULTS")

    output = pd.DataFrame([{
        "status": "WAITING_FOR_HPC_RESULTS",
        "temperature": "",
        "deformation": "",
        "reason": "Complete HPC simulation results first."
    }])

    output.to_csv(OUTPUT_FILE, index=False)

    raise SystemExit(0)


simulation = pd.read_csv(simulation_file)


# ---------------------------------------------------------
# 5. Merge datasets
# ---------------------------------------------------------

merged = simulation.merge(
    experimental_valid[
        [
            "temperature",
            "deformation",
            "experimental_Bulk_Modulus"
        ]
    ],
    on=["temperature", "deformation"],
    how="inner"
)


if len(merged) == 0:

    print()
    print("No matching simulation/experiment points found.")
    print("STATUS: WAITING_FOR_MATCHING_DATA")

    output = pd.DataFrame([{
        "status": "WAITING_FOR_MATCHING_DATA",
        "temperature": "",
        "deformation": "",
        "reason":
            "Simulation and experimental parameter points "
            "must overlap."
    }])

    output.to_csv(OUTPUT_FILE, index=False)

    raise SystemExit(0)


# ---------------------------------------------------------
# 6. Calculate simulation error
# ---------------------------------------------------------

merged["absolute_error"] = (
    merged["Bulk_Modulus"] -
    merged["experimental_Bulk_Modulus"]
).abs()


# ---------------------------------------------------------
# 7. Identify region with largest error
# ---------------------------------------------------------

worst = merged.sort_values(
    "absolute_error",
    ascending=False
).iloc[0]


print()
print("Largest observed disagreement:")
print(f"Temperature : {worst['temperature']} K")
print(f"Deformation : {worst['deformation']}")
print(f"Simulation  : {worst['Bulk_Modulus']}")
print(f"Experiment  : {worst['experimental_Bulk_Modulus']}")
print(f"Error       : {worst['absolute_error']}")


# ---------------------------------------------------------
# 8. Select untested candidate points
# ---------------------------------------------------------

tested = set(
    zip(
        simulation["temperature"],
        simulation["deformation"]
    )
)

candidates = doe[
    ~doe.apply(
        lambda row:
        (row["temperature"], row["deformation"]) in tested,
        axis=1
    )
].copy()


if len(candidates) == 0:

    print()
    print("All candidate points have already been simulated.")
    print("STATUS: DOE_COMPLETE")

    output = pd.DataFrame([{
        "status": "DOE_COMPLETE",
        "temperature": "",
        "deformation": "",
        "reason": "No untested candidate points remain."
    }])

    output.to_csv(OUTPUT_FILE, index=False)

    raise SystemExit(0)


# ---------------------------------------------------------
# 9. Find candidate closest to worst-error region
# ---------------------------------------------------------

temperature_range = doe["temperature"].max() - doe["temperature"].min()
deformation_range = doe["deformation"].max() - doe["deformation"].min()

if temperature_range == 0:
    temperature_range = 1

if deformation_range == 0:
    deformation_range = 1


candidates["distance"] = np.sqrt(
    (
        (candidates["temperature"] - worst["temperature"])
        / temperature_range
    ) ** 2
    +
    (
        (candidates["deformation"] - worst["deformation"])
        / deformation_range
    ) ** 2
)


next_point = candidates.sort_values(
    "distance"
).iloc[0]


# ---------------------------------------------------------
# 10. Save next simulation
# ---------------------------------------------------------

result = pd.DataFrame([{
    "status": "NEXT_SIMULATION_SELECTED",
    "temperature": next_point["temperature"],
    "deformation": next_point["deformation"],
    "reason":
        "Selected untested point near the region "
        "with the largest observed simulation/experiment error."
}])


result.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 60)
print("NEXT SIMULATION")
print("=" * 60)
print(f"Temperature : {next_point['temperature']} K")
print(f"Deformation : {next_point['deformation']}")
print()
print(f"Saved to: {OUTPUT_FILE}")
print("=" * 60)