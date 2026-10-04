import os
import pandas as pd
import matplotlib.pyplot as plt


PROJECT_FOLDER = r"C:\Users\Dell\Desktop\lammps-automation"

DATASET_FILE = os.path.join(
    PROJECT_FOLDER,
    "results",
    "simulation_dataset.csv"
)

REPORTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "reports"
)


os.makedirs(
    REPORTS_FOLDER,
    exist_ok=True
)


# Read simulation dataset

data = pd.read_csv(
    DATASET_FILE
)


# ------------------------------------------------------------
# Plot 1: Temperature vs Bulk Modulus
# ------------------------------------------------------------

plt.figure()

plt.plot(
    data["temperature"],
    data["Bulk_Modulus"],
    marker="o"
)

plt.xlabel(
    "Temperature (K)"
)

plt.ylabel(
    "Bulk Modulus (GPa)"
)

plt.title(
    "Temperature vs Bulk Modulus"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    os.path.join(
        REPORTS_FOLDER,
        "temperature_vs_bulk_modulus.png"
    ),
    dpi=200
)

plt.close()


# ------------------------------------------------------------
# Plot 2: Temperature vs Poisson Ratio
# ------------------------------------------------------------

plt.figure()

plt.plot(
    data["temperature"],
    data["Poisson_Ratio"],
    marker="o"
)

plt.xlabel(
    "Temperature (K)"
)

plt.ylabel(
    "Poisson Ratio"
)

plt.title(
    "Temperature vs Poisson Ratio"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    os.path.join(
        REPORTS_FOLDER,
        "temperature_vs_poisson_ratio.png"
    ),
    dpi=200
)

plt.close()


# ------------------------------------------------------------
# Plot 3: Temperature vs C11
# ------------------------------------------------------------

plt.figure()

plt.plot(
    data["temperature"],
    data["C11"],
    marker="o"
)

plt.xlabel(
    "Temperature (K)"
)

plt.ylabel(
    "C11 (GPa)"
)

plt.title(
    "Temperature vs C11"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    os.path.join(
        REPORTS_FOLDER,
        "temperature_vs_C11.png"
    ),
    dpi=200
)

plt.close()


print()
print("Dataset plots generated successfully.")

print()
print("Generated files:")

print(
    os.path.join(
        REPORTS_FOLDER,
        "temperature_vs_bulk_modulus.png"
    )
)

print(
    os.path.join(
        REPORTS_FOLDER,
        "temperature_vs_poisson_ratio.png"
    )
)

print(
    os.path.join(
        REPORTS_FOLDER,
        "temperature_vs_C11.png"
    )
)