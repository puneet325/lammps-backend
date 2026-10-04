import os
import json
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "results",
    "doe_dataset.csv"
)

OUTPUT_CSV = os.path.join(
    BASE_DIR,
    "results",
    "multiscale_material_properties.csv"
)

OUTPUT_JSON = os.path.join(
    BASE_DIR,
    "results",
    "multiscale_material_properties.json"
)


print("=" * 65)
print("ATOMISTIC -> MESOSCALE -> MACROSCALE BRIDGE")
print("=" * 65)


# ---------------------------------------------------------
# Load atomistic simulation results
# ---------------------------------------------------------

print("\nLoading atomistic simulation results...")

df = pd.read_csv(INPUT_FILE)

print(f"Simulation rows: {len(df)}")


# ---------------------------------------------------------
# Select properties needed by continuum models
# ---------------------------------------------------------

properties = df[
    [
        "temperature",
        "deformation",
        "C11",
        "C12",
        "C44",
        "Bulk_Modulus",
        "Poisson_Ratio"
    ]
].copy()


# ---------------------------------------------------------
# Add model metadata
# ---------------------------------------------------------

properties["source"] = "LAMMPS_atomistic_simulation"

properties["scale"] = "atomistic_to_continuum"

properties["material"] = "silicon"


# ---------------------------------------------------------
# Calculate isotropic-equivalent Young's modulus
#
# E = 3K(1 - 2nu)
#
# This is an equivalent isotropic value.
# Silicon is anisotropic, so this should not be
# interpreted as its complete elastic description.
# ---------------------------------------------------------

properties["Youngs_Modulus_Isotropic_Equivalent"] = (
    3
    * properties["Bulk_Modulus"]
    * (1 - 2 * properties["Poisson_Ratio"])
)


# ---------------------------------------------------------
# Rearrange columns
# ---------------------------------------------------------

properties = properties[
    [
        "material",
        "temperature",
        "deformation",
        "C11",
        "C12",
        "C44",
        "Bulk_Modulus",
        "Poisson_Ratio",
        "Youngs_Modulus_Isotropic_Equivalent",
        "source",
        "scale"
    ]
]


# ---------------------------------------------------------
# Save CSV
# ---------------------------------------------------------

properties.to_csv(
    OUTPUT_CSV,
    index=False
)


# ---------------------------------------------------------
# Save JSON
# ---------------------------------------------------------

records = properties.to_dict(
    orient="records"
)

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        records,
        f,
        indent=4
    )


print("\nMultiscale material-property table created:")

print(OUTPUT_CSV)

print("\nJSON interface created:")

print(OUTPUT_JSON)


print("\nExample material properties:")

print(
    properties.head().to_string(index=False)
)


print("\n" + "=" * 65)
print("MULTISCALE BRIDGE COMPLETED")
print("=" * 65)