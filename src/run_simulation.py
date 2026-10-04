import subprocess
import os

import sys


# ============================================================
# RUN ID
# ============================================================

RUN_ID = os.environ.get("LAMMPS_RUN_ID", "run_001")


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SIMULATION_FOLDER = os.path.join(PROJECT_FOLDER, "simulations", RUN_ID)

INPUT_FILE = os.path.join(SIMULATION_FOLDER, "in.elastic")
DUMP_FILE = os.path.join(SIMULATION_FOLDER, "dump.lammpstrj")


# ============================================================
# CHECK INPUT
# ============================================================

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"LAMMPS input file not found:\n{INPUT_FILE}")


# ============================================================
# ADD DUMP COMMAND IF THE INPUT FILE DOES NOT HAVE ONE
# (this is what creates dump.lammpstrj for OVITO)
# ============================================================

DUMP_COMMANDS = [
    "",
    "# Trajectory output for OVITO (added automatically)",
    "dump 1 all custom 10 dump.lammpstrj id type x y z",
    "dump_modify 1 first yes",
    "",
]


def add_dump_command(path):
    with open(path, "r", errors="ignore") as file:
        lines = file.read().splitlines()

    for line in lines:
        if line.strip().lower().startswith("dump "):
            print("Input already has a dump command. No change needed.")
            return

    # The dump must come after the atoms exist.
    markers = [
        r"^\s*include\s+\S*init",
        r"^\s*create_atoms\b",
        r"^\s*read_data\b",
        r"^\s*read_restart\b",
    ]

    insert_at = None

    for marker in markers:
        for index, line in enumerate(lines):
            if re.match(marker, line, re.IGNORECASE):
                insert_at = index + 1
                break

        if insert_at is not None:
            break

    if insert_at is None:
        raise RuntimeError(
            "Could not find where atoms are created in in.elastic. "
            "Add this line yourself after the atoms are created:\n"
            + DUMP_COMMANDS[2]
        )

    lines[insert_at:insert_at] = DUMP_COMMANDS

    with open(path, "w") as file:
        file.write("\n".join(lines) + "\n")

    print("Added dump command to in.elastic after line", insert_at)


add_dump_command(INPUT_FILE)


# ============================================================
# START
# ============================================================

print()
print("========================================")
print("      STARTING LAMMPS SIMULATION")
print("========================================")
print()
print("Run ID:", RUN_ID)
print("Working directory:", SIMULATION_FOLDER)
print("Input file:", INPUT_FILE)
print()


# ============================================================
# RUN LAMMPS
# ============================================================

result = subprocess.run(
    ["lmp", "-in", "in.elastic"],
    cwd=SIMULATION_FOLDER,
    capture_output=True,
    text=True,
)

print()
print("===== LAMMPS OUTPUT =====")
print()
print(result.stdout)

print()
print("===== LAMMPS ERRORS =====")
print()
print(result.stderr)

print()
print("Return code:", result.returncode)


# ============================================================
# RESULT
# ============================================================

if result.returncode != 0:
    print()
    print("Simulation failed.")
    sys.exit(result.returncode)

print()
print("Files in run folder:", os.listdir(SIMULATION_FOLDER))

if not os.path.exists(DUMP_FILE):
    print()
    print("ERROR: LAMMPS finished but dump.lammpstrj was not created.")
    sys.exit(1)

print()
print("Simulation completed successfully.")
print("Trajectory file:", DUMP_FILE)
