import os
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


# ============================================================
# PATHS
# ============================================================

PROJECT_FOLDER = (
    r"C:\Users\Dell\Desktop\lammps-automation"
)

SIMULATION_FILE = os.path.join(
    PROJECT_FOLDER,
    "results",
    "doe_dataset.csv"
)

EXPERIMENTAL_FILE = os.path.join(
    PROJECT_FOLDER,
    "inputs",
    "experimental_data.csv"
)

RESULTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "results"
)

REPORTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "reports"
)

MERGED_FILE = os.path.join(
    RESULTS_FOLDER,
    "merged_dataset.csv"
)

ML_RESULTS_FILE = os.path.join(
    RESULTS_FOLDER,
    "ml_results.csv"
)


# ============================================================
# CREATE FOLDERS
# ============================================================

os.makedirs(
    RESULTS_FOLDER,
    exist_ok=True
)

os.makedirs(
    REPORTS_FOLDER,
    exist_ok=True
)


# ============================================================
# LOAD SIMULATION DATA
# ============================================================

print()
print("=" * 65)
print("SIMULATION + EXPERIMENT + ML PIPELINE")
print("=" * 65)

print()
print("Loading simulation dataset...")

simulation = pd.read_csv(
    SIMULATION_FILE
)

simulation = simulation[
    simulation["status"] == "SUCCESS"
].copy()

print(
    f"Simulation rows: "
    f"{len(simulation)}"
)


# ============================================================
# LOAD EXPERIMENTAL DATA
# ============================================================

print()
print("Loading experimental dataset...")

experimental = pd.read_csv(
    EXPERIMENTAL_FILE
)

print(
    f"Experimental rows: "
    f"{len(experimental)}"
)


# ============================================================
# CHECK WHETHER REAL EXPERIMENTAL VALUES EXIST
# ============================================================

experimental_columns = [
    "experimental_C11",
    "experimental_Bulk_Modulus",
    "experimental_Poisson_Ratio"
]

has_experimental_data = (
    experimental[experimental_columns]
    .notna()
    .any()
    .any()
)


if not has_experimental_data:

    print()
    print(
        "No experimental measurements supplied yet."
    )

    print(
        "Creating simulation-only dataset."
    )

    print(
        "ML comparison will begin when real "
        "experimental measurements are added."
    )


# ============================================================
# MERGE DATA
# ============================================================

merged = pd.merge(
    simulation,
    experimental,
    on=[
        "temperature",
        "deformation"
    ],
    how="left"
)


merged.to_csv(
    MERGED_FILE,
    index=False
)


print()
print(
    "Merged dataset created:"
)

print(
    MERGED_FILE
)


# ============================================================
# ML DATASET
# ============================================================

# We train a model to predict Bulk Modulus
# from simulation parameters.

features = [
    "temperature",
    "deformation"
]

target = "Bulk_Modulus"


X = simulation[
    features
]

y = simulation[
    target
]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print()
print("Training ML model...")

if len(simulation) < 5:

    print(
        "Not enough simulation points for "
        "a meaningful train/test split."
    )

    print(
        "At least 5 points are recommended."
    )

else:

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.25,
            random_state=42
        )
    )


    # ========================================================
    # RANDOM FOREST
    # ========================================================

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )


    model.fit(
        X_train,
        y_train
    )


    predictions = model.predict(
        X_test
    )


    # ========================================================
    # METRICS
    # ========================================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )


    print()
    print("=" * 65)
    print("ML RESULTS")
    print("=" * 65)

    print()

    print(
        f"MAE  : {mae:.6f}"
    )

    print(
        f"RMSE : {rmse:.6f}"
    )

    print(
        f"R2   : {r2:.6f}"
    )


    # ========================================================
    # SAVE PREDICTIONS
    # ========================================================

    ml_results = X_test.copy()

    ml_results[
        "actual_Bulk_Modulus"
    ] = y_test.values

    ml_results[
        "predicted_Bulk_Modulus"
    ] = predictions


    ml_results[
        "absolute_error"
    ] = abs(
        ml_results[
            "actual_Bulk_Modulus"
        ]
        -
        ml_results[
            "predicted_Bulk_Modulus"
        ]
    )


    ml_results.to_csv(
        ML_RESULTS_FILE,
        index=False
    )


    print()

    print(
        "ML prediction dataset:"
    )

    print(
        ML_RESULTS_FILE
    )


    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    print()
    print("Feature importance:")

    for feature, importance in zip(
        features,
        model.feature_importances_
    ):

        print(
            f"{feature}: "
            f"{importance:.6f}"
        )


print()
print("=" * 65)
print("ML PIPELINE COMPLETED")
print("=" * 65)