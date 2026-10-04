import os
import itertools
import pandas as pd
import numpy as np


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "results",
    "doe_300_points.csv"
)


# ---------------------------------------------------------
# DoE definition
# ---------------------------------------------------------

TEMPERATURES = np.linspace(
    300,
    1200,
    20
)

DEFORMATIONS = np.linspace(
    0.01,
    0.03,
    15
)


# ---------------------------------------------------------
# Generate combinations
# ---------------------------------------------------------

rows = []

run_id = 1

for temperature, deformation in itertools.product(
    TEMPERATURES,
    DEFORMATIONS
):

    rows.append({
        "run_id": f"DOE_{run_id:03d}",
        "temperature": round(float(temperature), 3),
        "deformation": round(float(deformation), 5),
        "status": "PLANNED"
    })

    run_id += 1


df = pd.DataFrame(rows)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 65)
print("300-POINT DESIGN OF EXPERIMENTS")
print("=" * 65)

print()
print(f"Temperature points : {len(TEMPERATURES)}")
print(f"Deformation points  : {len(DEFORMATIONS)}")
print(f"Total simulations   : {len(df)}")

print()
print("Temperature range:")
print(
    f"{TEMPERATURES.min():.1f} K -> "
    f"{TEMPERATURES.max():.1f} K"
)

print()
print("Deformation range:")
print(
    f"{DEFORMATIONS.min():.5f} -> "
    f"{DEFORMATIONS.max():.5f}"
)

print()
print("Dataset:")
print(OUTPUT_FILE)

print()
print("First 10 points:")
print(df.head(10).to_string(index=False))

print()
print("Last 5 points:")
print(df.tail(5).to_string(index=False))

print()
print("=" * 65)
print("300-POINT DOE CREATED")
print("=" * 65)