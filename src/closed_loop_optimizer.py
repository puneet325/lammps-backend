from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

EXPERIMENT_FILE = ROOT / "inputs" / "experimental_data.csv"
DOE_FILE = ROOT / "results" / "doe_300_points.csv"
OUTPUT_FILE = ROOT / "results" / "closed_loop_optimizer.csv"


print("=" * 60)
print("CLOSED LOOP PARAMETER OPTIMIZER")
print("=" * 60)


# ---------------------------------------------------------
# 1. Load experimental data
# ---------------------------------------------------------

if not EXPERIMENT_FILE.exists():
    print("Experimental data file not found.")
    raise SystemExit(1)

experimental = pd.read_csv(EXPERIMENT_FILE)

print(f"Experimental rows: {len(experimental)}")


# ---------------------------------------------------------
# 2. Check whether real measurements exist
# ---------------------------------------------------------

measurement_columns = [
    "experimental_C11",
    "experimental_Bulk_Modulus",
    "experimental_Poisson_Ratio"
]

has_experimental_data = experimental[measurement_columns].notna().any().any()


if not has_experimental_data:

    print()
    print("Experimental measurements: NOT AVAILABLE")
    print()
    print("STATUS: WAITING_FOR_EXPERIMENT")
    print()
    print("No parameter adjustment performed.")
    print("Add real experimental measurements to:")
    print()
    print(EXPERIMENT_FILE)
    print()

    output = pd.DataFrame({
        "status": ["WAITING_FOR_EXPERIMENT"],
        "message": [
            "Real experimental measurements are required "
            "before automatic parameter adjustment."
        ]
    })

    output.to_csv(OUTPUT_FILE, index=False)

    print(f"Status saved to: {OUTPUT_FILE}")

    raise SystemExit(0)


# ---------------------------------------------------------
# 3. Load 300-point candidate space
# ---------------------------------------------------------

if not DOE_FILE.exists():
    print("300-point DoE file not found.")
    raise SystemExit(1)

doe = pd.read_csv(DOE_FILE)

print(f"Candidate parameter points: {len(doe)}")


# ---------------------------------------------------------
# 4. Merge available experimental information
# ---------------------------------------------------------

merged = doe.merge(
    experimental,
    on=["temperature", "deformation"],
    how="left"
)


# ---------------------------------------------------------
# 5. Calculate errors where measurements exist
# ---------------------------------------------------------

merged["Bulk_Error"] = (
    merged["Bulk_Modulus"] -
    merged["experimental_Bulk_Modulus"]
).abs()


valid = merged.dropna(subset=["experimental_Bulk_Modulus"])


if len(valid) == 0:

    print()
    print("No matching experimental measurements found.")
    print("STATUS: WAITING_FOR_EXPERIMENT")

    output = pd.DataFrame({
        "status": ["WAITING_FOR_EXPERIMENT"],
        "message": [
            "Experimental values do not yet match "
            "the simulation parameter space."
        ]
    })

    output.to_csv(OUTPUT_FILE, index=False)

    raise SystemExit(0)


# ---------------------------------------------------------
# 6. Find largest disagreement
# ---------------------------------------------------------

worst = valid.sort_values(
    "Bulk_Error",
    ascending=False
).iloc[0]


print()
print("Largest simulation/experiment disagreement:")
print(f"Temperature : {worst['temperature']}")
print(f"Deformation : {worst['deformation']}")
print(f"Simulation Bulk Modulus : {worst['Bulk_Modulus']}")
print(
    f"Experimental Bulk Modulus : "
    f"{worst['experimental_Bulk_Modulus']}"
)
print(f"Absolute error : {worst['Bulk_Error']}")


# ---------------------------------------------------------
# 7. Save recommendation
# ---------------------------------------------------------

recommendation = pd.DataFrame([{
    "status": "PARAMETER_ADJUSTMENT_REQUIRED",
    "temperature": worst["temperature"],
    "deformation": worst["deformation"],
    "simulation_bulk_modulus": worst["Bulk_Modulus"],
    "experimental_bulk_modulus": worst[
        "experimental_Bulk_Modulus"
    ],
    "absolute_error": worst["Bulk_Error"],
    "recommended_action":
        "Investigate parameters around the region "
        "with the largest simulation/experiment error."
}])

recommendation.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("Recommendation saved to:")
print(OUTPUT_FILE)

print()
print("=" * 60)
print("CLOSED LOOP STEP COMPLETE")
print("=" * 60)