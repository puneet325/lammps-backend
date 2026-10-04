import os
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

SIM_FILE = os.path.join(
    BASE_DIR,
    "results",
    "doe_dataset.csv"
)

CANDIDATE_FILE = os.path.join(
    BASE_DIR,
    "results",
    "doe_300_points.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "results",
    "recommended_experiments.csv"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

NUMBER_OF_EXPERIMENTS = 12

FEATURES = [
    "temperature",
    "deformation"
]

TARGET = "Bulk_Modulus"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("=" * 65)
print("AUTOMATIC EXPERIMENTAL-POINT SELECTION")
print("=" * 65)

print("\nLoading existing simulations...")

simulation = pd.read_csv(SIM_FILE)

print(
    f"Existing simulation points: "
    f"{len(simulation)}"
)


print("\nLoading 300-point candidate space...")

candidates = pd.read_csv(CANDIDATE_FILE)

print(
    f"Candidate points: "
    f"{len(candidates)}"
)


# ---------------------------------------------------------
# Train surrogate model
# ---------------------------------------------------------

print("\nTraining surrogate model...")

X = simulation[FEATURES]

y = simulation[TARGET]

model = RandomForestRegressor(
    n_estimators=300,
    random_state=42
)

model.fit(X, y)


# ---------------------------------------------------------
# Predict all 300 candidate points
# ---------------------------------------------------------

candidates["predicted_Bulk_Modulus"] = model.predict(
    candidates[FEATURES]
)


# ---------------------------------------------------------
# Normalize features and predicted response
# ---------------------------------------------------------

selection_features = [
    "temperature",
    "deformation",
    "predicted_Bulk_Modulus"
]

scaler = MinMaxScaler()

normalized = scaler.fit_transform(
    candidates[selection_features]
)


# ---------------------------------------------------------
# Farthest-point sampling
# ---------------------------------------------------------

selected_indices = []

# Start with the point closest to the center
center = normalized.mean(axis=0)

first_index = np.argmin(
    np.linalg.norm(
        normalized - center,
        axis=1
    )
)

selected_indices.append(first_index)


while len(selected_indices) < NUMBER_OF_EXPERIMENTS:

    selected_points = normalized[
        selected_indices
    ]

    best_index = None
    best_distance = -1

    for i in range(len(normalized)):

        if i in selected_indices:
            continue

        distances = np.linalg.norm(
            normalized[i] - selected_points,
            axis=1
        )

        minimum_distance = distances.min()

        if minimum_distance > best_distance:
            best_distance = minimum_distance
            best_index = i

    selected_indices.append(best_index)


# ---------------------------------------------------------
# Create experimental recommendation
# ---------------------------------------------------------

selected = candidates.iloc[
    selected_indices
].copy()


selected = selected.sort_values(
    ["temperature", "deformation"]
)


selected.insert(
    0,
    "experiment_id",
    [
        f"EXP_{i:02d}"
        for i in range(1, len(selected) + 1)
    ]
)


selected["experimental_status"] = "PLANNED"


selected["reason"] = (
    "Representative point selected "
    "from 300-point simulation design"
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

selected.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Print
# ---------------------------------------------------------

print("\nRecommended experimental points:")

print(
    selected[
        [
            "experiment_id",
            "temperature",
            "deformation",
            "predicted_Bulk_Modulus"
        ]
    ].to_string(index=False)
)


print("\nSaved:")

print(OUTPUT_FILE)

print()
print("=" * 65)
print("EXPERIMENTAL SELECTION COMPLETED")
print("=" * 65)