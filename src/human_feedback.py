import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SIM_FILE = os.path.join(BASE_DIR, "results", "doe_dataset.csv")
EXP_FILE = os.path.join(BASE_DIR, "inputs", "experimental_data.csv")

FEEDBACK_FILE = os.path.join(BASE_DIR, "results", "expert_feedback.csv")
LOOP_FILE = os.path.join(BASE_DIR, "results", "closed_loop_recommendation.csv")


print("=" * 65)
print("HUMAN FEEDBACK + CLOSED LOOP PIPELINE")
print("=" * 65)

# ---------------------------------------------------------
# Load simulation data
# ---------------------------------------------------------

print("\nLoading simulation data...")

sim = pd.read_csv(SIM_FILE)

print(f"Simulation rows: {len(sim)}")


# ---------------------------------------------------------
# Load experimental data
# ---------------------------------------------------------

print("\nLoading experimental data...")

exp = pd.read_csv(EXP_FILE)

print(f"Experimental rows: {len(exp)}")


# ---------------------------------------------------------
# Check experimental measurements
# ---------------------------------------------------------

target_columns = [
    "experimental_C11",
    "experimental_Bulk_Modulus",
    "experimental_Poisson_Ratio"
]

available_targets = []

for column in target_columns:
    if column in exp.columns:
        if exp[column].notna().any():
            available_targets.append(column)


# ---------------------------------------------------------
# No experimental data yet
# ---------------------------------------------------------

if not available_targets:

    print("\nNo experimental measurements are available yet.")

    print("\nCreating expert feedback template...")

    feedback = pd.DataFrame({
        "temperature": [300, 600, 900, 1200],
        "deformation": [0.02, 0.02, 0.02, 0.02],
        "property": ["Bulk_Modulus"] * 4,
        "feedback": ["PENDING"] * 4,
        "suggested_action": ["WAIT_FOR_EXPERIMENT"] * 4,
        "expert_comment": [""] * 4
    })

    feedback.to_csv(FEEDBACK_FILE, index=False)

    recommendation = pd.DataFrame({
        "status": ["WAITING_FOR_EXPERIMENT"],
        "message": [
            "Add real experimental measurements before calibration."
        ]
    })

    recommendation.to_csv(LOOP_FILE, index=False)

    print(f"\nFeedback template:")
    print(FEEDBACK_FILE)

    print(f"\nClosed-loop recommendation:")
    print(LOOP_FILE)

    print("\n" + "=" * 65)
    print("PIPELINE WAITING FOR EXPERIMENTAL DATA")
    print("=" * 65)

    raise SystemExit


# ---------------------------------------------------------
# Merge simulation and experimental data
# ---------------------------------------------------------

print("\nExperimental measurements detected.")

merged = sim.merge(
    exp,
    on=["temperature", "deformation"],
    how="inner"
)

print(f"Matched experimental/simulation rows: {len(merged)}")


# ---------------------------------------------------------
# Calculate errors
# ---------------------------------------------------------

if "experimental_Bulk_Modulus" in merged.columns:

    merged["Bulk_Modulus_Error"] = (
        merged["Bulk_Modulus"]
        - merged["experimental_Bulk_Modulus"]
    )

    merged["Absolute_Error"] = (
        merged["Bulk_Modulus_Error"].abs()
    )


# ---------------------------------------------------------
# Generate expert feedback
# ---------------------------------------------------------

feedback_rows = []

for _, row in merged.iterrows():

    error = row["Bulk_Modulus_Error"]

    if abs(error) < 1.0:

        feedback = "ACCEPTABLE"
        action = "KEEP_PARAMETERS"

    elif error > 0:

        feedback = "SIMULATION_HIGH"
        action = "REDUCE_PARAMETER_EFFECT"

    else:

        feedback = "SIMULATION_LOW"
        action = "INCREASE_PARAMETER_EFFECT"

    feedback_rows.append({
        "temperature": row["temperature"],
        "deformation": row["deformation"],
        "property": "Bulk_Modulus",
        "simulation_value": row["Bulk_Modulus"],
        "experimental_value": row["experimental_Bulk_Modulus"],
        "error": error,
        "feedback": feedback,
        "suggested_action": action,
        "expert_comment": ""
    })


feedback_df = pd.DataFrame(feedback_rows)

feedback_df.to_csv(FEEDBACK_FILE, index=False)


# ---------------------------------------------------------
# Find closest simulation to experiment
# ---------------------------------------------------------

if len(merged) > 0:

    best = merged.loc[
        merged["Absolute_Error"].idxmin()
    ]

    recommendation = pd.DataFrame({
        "status": ["CALIBRATION_POINT_FOUND"],
        "temperature": [best["temperature"]],
        "deformation": [best["deformation"]],
        "simulation_bulk_modulus": [best["Bulk_Modulus"]],
        "experimental_bulk_modulus": [
            best["experimental_Bulk_Modulus"]
        ],
        "absolute_error": [best["Absolute_Error"]]
    })

else:

    recommendation = pd.DataFrame({
        "status": ["NO_MATCHING_POINTS"],
        "message": [
            "No simulation and experiment parameter combinations matched."
        ]
    })


recommendation.to_csv(
    LOOP_FILE,
    index=False
)


# ---------------------------------------------------------
# Print results
# ---------------------------------------------------------

print("\nExpert feedback generated:")
print(FEEDBACK_FILE)

print("\nClosed-loop recommendation generated:")
print(LOOP_FILE)

print("\n" + "=" * 65)
print("HUMAN FEEDBACK PIPELINE COMPLETED")
print("=" * 65)