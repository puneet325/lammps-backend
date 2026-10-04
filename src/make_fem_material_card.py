import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "results" / "properties.csv"
OUT = ROOT / "results" / "fem_material_card.json"

values = {}
with PROPS.open() as fh:
    for row in csv.DictReader(fh):
        try:
            values[row["Property"]] = float(row["Value"])
        except ValueError:
            pass

K = values["Bulk Modulus"]
nu = values["Poisson Ratio"]
E = 3 * K * (1 - 2 * nu)
G = E / (2 * (1 + nu))

card = {
    "material": "Silicon",
    "source": "LAMMPS atomistic elastic calculation",
    "state": {"temperature_K": 300, "deformation": 0.02},
    "isotropic_equivalent": {
        "Youngs_modulus_GPa": E,
        "Poisson_ratio": nu,
        "Shear_modulus_GPa": G,
        "Bulk_modulus_GPa": K
    },
    "anisotropic_single_crystal_constants_GPa": {
        "C11": values["C11"],
        "C12": values["C12"],
        "C44": values["C44"]
    },
    "warning": "Silicon is anisotropic. The isotropic values are an equivalent engineering representation, not a replacement for a full crystal anisotropic constitutive law."
}

with OUT.open("w") as fh:
    json.dump(card, fh, indent=2)

print("Created:", OUT)
print(json.dumps(card, indent=2))
