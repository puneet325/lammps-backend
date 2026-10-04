import subprocess
import os
import sys


# ============================================================
# RUN ID
# ============================================================

RUN_ID = os.environ.get(
    "LAMMPS_RUN_ID",
    "run_001"
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# SIMULATION FOLDER
# ============================================================

SIMULATION_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "simulations",
    RUN_ID
)


INPUT_FILE = os.path.join(
    SIMULATION_FOLDER,
    "in.elastic"
)


# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.exists(
    INPUT_FILE
):

    raise FileNotFoundError(
        f"LAMMPS input file not found:\n"
        f"{INPUT_FILE}"
    )


# ============================================================
# LAMMPS COMMAND
# ============================================================

command = [
    "lmp",
    "-in",
    "in.elastic"
]


# ============================================================
# START
# ============================================================

print()
print("========================================")
print("      STARTING LAMMPS SIMULATION")
print("========================================")
print()

print(
    "Run ID:",
    RUN_ID
)

print(
    "Working directory:",
    SIMULATION_FOLDER
)

print(
    "Input file:",
    INPUT_FILE
)

print()


# ============================================================
# RUN LAMMPS
# ============================================================

result = subprocess.run(
    command,
    cwd=SIMULATION_FOLDER,
    capture_output=True,
    text=True
)


# ============================================================
# OUTPUT
# ============================================================

print()
print("===== LAMMPS OUTPUT =====")
print()

print(
    result.stdout
)


print()
print("===== LAMMPS ERRORS =====")
print()

print(
    result.stderr
)


print()
print(
    "Return code:",
    result.returncode
)


# ============================================================
# RESULT
# ============================================================

if result.returncode == 0:

    print()
    print(
        "Simulation completed successfully."
    )

else:

    print()
    print(
        "Simulation failed."
    )

    sys.exit(
        result.returncode
    )