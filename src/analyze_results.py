import os
import re
import csv
import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# RUN ID
# ============================================================

RUN_ID = os.environ.get(
    "LAMMPS_RUN_ID",
    "run_001"
)

SIMULATION_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "simulations",
    RUN_ID
)

LOG_FILE = os.path.join(
    SIMULATION_FOLDER,
    "log.lammps"
)

RESULTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "results"
)

REPORTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "reports"
)


# ============================================================
# OUTPUT FILES
# ============================================================

PROPERTIES_FILE = os.path.join(
    RESULTS_FOLDER,
    "properties.csv"
)

GRAPH_FILE = os.path.join(
    REPORTS_FOLDER,
    "elastic_constants.png"
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
# START
# ============================================================

print()
print("========================================")
print("      LAMMPS RESULT ANALYSIS")
print("========================================")
print()

print("Run ID:", RUN_ID)
print("Simulation folder:", SIMULATION_FOLDER)
print("Log file:", LOG_FILE)
print()


# ============================================================
# CHECK LOG FILE
# ============================================================

if not os.path.exists(LOG_FILE):

    raise FileNotFoundError(
        f"LAMMPS log file not found:\n{LOG_FILE}"
    )


# ============================================================
# READ LOG FILE
# ============================================================

with open(
    LOG_FILE,
    "r",
    errors="ignore"
) as file:

    log_data = file.read()


# ============================================================
# PROPERTIES TO EXTRACT
# ============================================================

property_names = [
    "C11",
    "C22",
    "C33",
    "C12",
    "C13",
    "C23",
    "C44",
    "C55",
    "C66",
    "Bulk Modulus",
    "Shear Modulus 1",
    "Shear Modulus 2",
    "Poisson Ratio"
]


# ============================================================
# EXTRACTION FUNCTION
# ============================================================

def extract_property(name):

    if name.startswith("C"):

        pattern = (
            r"Elastic Constant\s+"
            + re.escape(name)
            + r"all\s*=\s*"
            r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
        )

    else:

        pattern = (
            re.escape(name)
            + r"\s*=\s*"
            r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
        )

    match = re.search(
        pattern,
        log_data,
        re.IGNORECASE
    )

    if match:

        return float(
            match.group(1)
        )

    return None


# ============================================================
# EXTRACT VALUES
# ============================================================

results = {}

for name in property_names:

    value = extract_property(name)

    if value is not None:

        results[name] = value


# ============================================================
# CHECK REQUIRED VALUES
# ============================================================

required_constants = [
    "C11",
    "C22",
    "C33",
    "C12",
    "C13",
    "C23",
    "C44",
    "C55",
    "C66"
]

missing = []

for name in required_constants:

    if name not in results:

        missing.append(name)


if missing:

    raise RuntimeError(
        "Could not extract these elastic constants "
        "from log.lammps:\n"
        + ", ".join(missing)
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("===== LAMMPS ELASTIC PROPERTIES =====")
print()

print(
    f"{'Property':>18} {'Value':>14}"
)

print("-" * 34)

for name in property_names:

    if name in results:

        print(
            f"{name:>18} "
            f"{results[name]:14.6f}"
        )

print()


# ============================================================
# SAVE CSV
# ============================================================

with open(
    PROPERTIES_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "Property",
            "Value",
            "Unit"
        ]
    )

    for name in property_names:

        if name in results:

            writer.writerow(
                [
                    name,
                    results[name],
                    "GPa"
                    if name != "Poisson Ratio"
                    else ""
                ]
            )


print(
    "Results saved to:",
    PROPERTIES_FILE
)

print()


# ============================================================
# VALUES FOR GRAPH
# ============================================================

elastic_names = [
    "C11",
    "C22",
    "C33",
    "C12",
    "C13",
    "C23",
    "C44",
    "C55",
    "C66"
]

elastic_values = [
    results[name]
    for name in elastic_names
]


print("===== VALUES USED FOR GRAPH =====")

for name in elastic_names:

    print(
        f"{name} = "
        f"{results[name]:.12f} GPa"
    )

print()


# ============================================================
# CREATE GRAPH
# ============================================================

plt.figure(
    figsize=(12, 7)
)

plt.bar(
    elastic_names,
    elastic_values
)

plt.xlabel(
    "Elastic Constant"
)

plt.ylabel(
    "Value (GPa)"
)

plt.title(
    f"LAMMPS Elastic Constants - {RUN_ID}"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    GRAPH_FILE,
    dpi=200
)

plt.close()


# ============================================================
# COMPLETE
# ============================================================

print(
    "Elastic constants graph generated successfully."
)

print(
    "Saved to:",
    GRAPH_FILE
)

print()

print("========================================")
print("       ANALYSIS COMPLETE")
print("========================================")
print()

print("Run ID:", RUN_ID)