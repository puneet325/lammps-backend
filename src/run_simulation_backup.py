import subprocess
import os

# ------------------------------------------------------------
# Simulation paths
# ------------------------------------------------------------

simulation_folder = r"C:\Users\Dell\Desktop\lammps-automation\simulations\run_001"

input_file = os.path.join(
    simulation_folder,
    "in.elastic"
)


# ------------------------------------------------------------
# Check input file
# ------------------------------------------------------------

if not os.path.exists(input_file):
    raise FileNotFoundError(
        f"LAMMPS input file not found:\n{input_file}"
    )


# ------------------------------------------------------------
# LAMMPS command
# ------------------------------------------------------------

command = [
    "lmp",
    "-in",
    "in.elastic"
]

print("\n========================================")
print("STARTING LAMMPS SIMULATION")
print("========================================")

print(f"Working directory: {simulation_folder}")
print(f"Input file: {input_file}")


# ------------------------------------------------------------
# Run LAMMPS
# ------------------------------------------------------------

result = subprocess.run(
    command,
    cwd=simulation_folder,
    capture_output=True,
    text=True
)


# ------------------------------------------------------------
# Display output
# ------------------------------------------------------------

print("\n===== LAMMPS OUTPUT =====")
print(result.stdout)

print("\n===== LAMMPS ERRORS =====")
print(result.stderr)

print("\nReturn code:", result.returncode)


# ------------------------------------------------------------
# Result
# ------------------------------------------------------------

if result.returncode == 0:

    print("\nSimulation completed successfully.")

else:

    print("\nSimulation failed.")