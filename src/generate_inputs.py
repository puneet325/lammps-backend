import json
import os
import shutil
import re


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

PARAMETERS_FILE = os.path.join(
    PROJECT_FOLDER,
    "inputs",
    "parameters.json"
)

LAMMPS_EXAMPLE_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "HPC",
    "project",
    "lammps_examples"
)


# ============================================================
# GET RUN ID
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


# ============================================================
# CREATE SIMULATION FOLDER
# ============================================================

os.makedirs(
    SIMULATION_FOLDER,
    exist_ok=True
)


# ============================================================
# READ PARAMETERS
# ============================================================

if not os.path.exists(PARAMETERS_FILE):
    raise FileNotFoundError(
        f"Parameters file not found: {PARAMETERS_FILE}"
    )

with open(PARAMETERS_FILE, "r") as file:
    parameters = json.load(file)


temperature = parameters["temperature"]
deformation = parameters["deformation"]
strain_rate = parameters["strain_rate"]
material = parameters["materials"]


print()
print("========================================")
print("       SIMULATION PARAMETERS")
print("========================================")
print(f"Run ID       : {RUN_ID}")
print(f"Material     : {material}")
print(f"Temperature  : {temperature} K")
print(f"Deformation  : {deformation}")
print(f"Strain rate  : {strain_rate}")
print()


# ============================================================
# CURRENTLY SUPPORTED TEMPLATE
# ============================================================

if material.lower() != "silicon":
    raise ValueError(
        "Currently only Silicon is connected to the existing "
        "LAMMPS template. Additional materials require their "
        "own simulation templates."
    )


# ============================================================
# CHECK TEMPLATE FOLDER
# ============================================================

if not os.path.exists(LAMMPS_EXAMPLE_FOLDER):
    raise FileNotFoundError(
        f"LAMMPS template folder not found: "
        f"{LAMMPS_EXAMPLE_FOLDER}"
    )


# ============================================================
# COPY LAMMPS TEMPLATE FILES
# ============================================================

files_to_copy = [
    "in.elastic",
    "init.mod",
    "potential.mod",
    "displace.mod",
    "Si.sw"
]

for filename in files_to_copy:

    source = os.path.join(
        LAMMPS_EXAMPLE_FOLDER,
        filename
    )

    destination = os.path.join(
        SIMULATION_FOLDER,
        filename
    )

    if not os.path.exists(source):
        raise FileNotFoundError(
            f"Required template file not found: {source}"
        )

    shutil.copy2(
        source,
        destination
    )


# ============================================================
# UPDATE PARAMETERS IN init.mod
# ============================================================

init_file = os.path.join(
    SIMULATION_FOLDER,
    "init.mod"
)

with open(init_file, "r") as file:
    content = file.read()


# Temperature
content = re.sub(
    r"variable\s+temp\s+equal\s+[^\n]+",
    f"variable temp equal {temperature} # temperature from parameters.json",
    content
)


# Deformation
content = re.sub(
    r"variable\s+up\s+equal\s+[^\n]+",
    f"variable up equal {deformation}",
    content
)


# Strain rate
content = re.sub(
    r"variable\s+erate\s+equal\s+[^\n]+",
    f"variable erate equal {strain_rate}",
    content
)


with open(init_file, "w") as file:
    file.write(content)


# ============================================================
# VERIFY GENERATED VALUES
# ============================================================

with open(init_file, "r") as file:
    generated_content = file.read()


if f"variable up equal {deformation}" not in generated_content:
    raise RuntimeError(
        "Deformation parameter was not correctly written "
        "to init.mod"
    )


if f"variable temp equal {temperature}" not in generated_content:
    raise RuntimeError(
        "Temperature parameter was not correctly written "
        "to init.mod"
    )


print("Input parameters successfully applied.")
print(f"Temperature : {temperature}")
print(f"Deformation: {deformation}")
print(f"Strain rate: {strain_rate}")
print()


# ============================================================
# COMPLETE
# ============================================================

print("========================================")
print("       INPUT GENERATION COMPLETE")
print("========================================")
print()
print(f"Simulation folder:")
print(SIMULATION_FOLDER)
print()