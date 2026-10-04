import json
import os
import shutil
import re


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_FOLDER = r"C:\Users\Dell\Desktop\lammps-automation"

PARAMETERS_FILE = os.path.join(
    PROJECT_FOLDER,
    "inputs",
    "parameters.json"
)

LAMMPS_EXAMPLE_FOLDER = (
    r"C:\Users\Dell\Desktop\lammps"
    r"\examples\ELASTIC_T\DEFORMATION\Silicon"
)


# ============================================================
# GET RUN ID
# ============================================================

RUN_ID = os.environ.get("LAMMPS_RUN_ID", "run_001")

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
        "own LAMMPS templates and potentials."
    )


# ============================================================
# COPY COMPLETE LAMMPS EXAMPLE
# ============================================================

if not os.path.exists(LAMMPS_EXAMPLE_FOLDER):
    raise FileNotFoundError(
        f"LAMMPS example folder not found:\n"
        f"{LAMMPS_EXAMPLE_FOLDER}"
    )

print("Copying LAMMPS example...")

shutil.copytree(
    LAMMPS_EXAMPLE_FOLDER,
    SIMULATION_FOLDER,
    dirs_exist_ok=True
)


# ============================================================
# PARAMETERIZE init.mod
# ============================================================

init_file = os.path.join(
    SIMULATION_FOLDER,
    "init.mod"
)

if not os.path.exists(init_file):
    raise FileNotFoundError(
        f"init.mod not found:\n{init_file}"
    )


with open(init_file, "r") as file:
    init_data = file.read()


# ============================================================
# REPLACE TEMPERATURE
# ============================================================

temperature_pattern = (
    r"variable\s+temp\s+equal\s+[0-9.eE+-]+"
)

temperature_replacement = (
    f"variable temp equal {temperature}"
)

new_init_data, temp_replacements = re.subn(
    temperature_pattern,
    temperature_replacement,
    init_data,
    count=1
)

if temp_replacements != 1:
    raise RuntimeError(
        "Could not find the temperature variable in init.mod."
    )


# ============================================================
# REPLACE DEFORMATION
# ============================================================

deformation_pattern = (
    r"variable\s+up\s+equal\s+[0-9.eE+-]+"
)

deformation_replacement = (
    f"variable up equal {deformation}"
)

new_init_data, deformation_replacements = re.subn(
    deformation_pattern,
    deformation_replacement,
    new_init_data,
    count=1
)

if deformation_replacements != 1:
    raise RuntimeError(
        "Could not find the deformation variable 'up' in init.mod."
    )


# ============================================================
# WRITE MODIFIED init.mod
# ============================================================

with open(init_file, "w") as file:
    file.write(new_init_data)


# ============================================================
# VERIFY
# ============================================================

print()
print("LAMMPS input parameterized successfully.")

with open(init_file, "r") as file:

    for line in file:

        if line.strip().startswith(
            "variable temp equal"
        ):
            print("Verified:", line.strip())

        if line.strip().startswith(
            "variable up equal"
        ):
            print("Verified:", line.strip())


print()
print("Simulation folder:")
print(os.path.abspath(SIMULATION_FOLDER))

print()
print("Input generation completed.")