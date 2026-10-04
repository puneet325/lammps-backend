import subprocess
import sys
import os


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# RUN ID
# ============================================================

RUN_ID = os.environ.get(
    "LAMMPS_RUN_ID",
    "run_001"
)


# ============================================================
# PYTHON ENVIRONMENTS
# ============================================================

MAIN_PYTHON = os.path.join(
    PROJECT_FOLDER,
    ".venv",
    "Scripts",
    "python.exe"
)

OVITO_PYTHON = os.path.join(
    PROJECT_FOLDER,
    "ovito-env",
    "Scripts",
    "python.exe"
)


# ============================================================
# DISPLAY
# ============================================================

print()
print("============================================================")
print("              LAMMPS AUTOMATION PIPELINE")
print("============================================================")
print()

print("RUN ID:", RUN_ID)

print()

print("Pipeline:")
print()
print("INPUT GENERATION")
print("      ↓")
print("LAMMPS SIMULATION")
print("      ↓")
print("RESULT ANALYSIS")
print("      ↓")
print("OVITO VISUALIZATION")
print()

print("============================================================")
print()


# ============================================================
# ENVIRONMENT
# ============================================================

pipeline_environment = os.environ.copy()

pipeline_environment[
    "LAMMPS_RUN_ID"
] = RUN_ID


# ============================================================
# RUN FUNCTION
# ============================================================

def run_step(
    name,
    python_executable,
    script
):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)
    print()

    command = [
        python_executable,
        os.path.join(
            PROJECT_FOLDER,
            script
        )
    ]

    result = subprocess.run(
        command,
        cwd=PROJECT_FOLDER,
        env=pipeline_environment,
        capture_output=True,
        text=True
    )

    if result.stdout:

        print(
            result.stdout
        )

    if result.stderr:

        print(
            "ERROR OUTPUT:"
        )

        print(
            result.stderr
        )

    if result.returncode != 0:

        print()
        print(
            f"{name} FAILED"
        )

        print(
            "Return code:",
            result.returncode
        )

        sys.exit(
            result.returncode
        )

    print()
    print(
        f"{name} completed successfully."
    )


# ============================================================
# STEP 1
# ============================================================

run_step(
    "STEP 1: GENERATING INPUT",
    MAIN_PYTHON,
    "src/generate_inputs.py"
)


# ============================================================
# STEP 2
# ============================================================

run_step(
    "STEP 2: RUNNING LAMMPS",
    MAIN_PYTHON,
    "src/run_simulation.py"
)


# ============================================================
# STEP 3
# ============================================================

run_step(
    "STEP 3: ANALYZING RESULTS",
    MAIN_PYTHON,
    "src/analyze_results.py"
)


# ============================================================
# STEP 4
# ============================================================

run_step(
    "STEP 4: OVITO VISUALIZATION",
    OVITO_PYTHON,
    "src/Visualize.py"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print()
print("============================================================")
print("             FULL PIPELINE COMPLETED")
print("============================================================")
print()

print(
    "Run ID:",
    RUN_ID
)

print()

print(
    "Input generation       : COMPLETED"
)

print(
    "LAMMPS simulation      : COMPLETED"
)

print(
    "Result analysis        : COMPLETED"
)

print(
    "OVITO visualization    : COMPLETED"
)

print()

print("Generated outputs:")
print()
print("    results/properties.csv")
print("    results/deformation_results.csv")
print("    reports/elastic_constants.png")
print("    reports/ovito_deformation.png")
print("    reports/visualization_summary.txt")

print()

print("Simulation data:")
print(
    f"    simulations/{RUN_ID}/"
)

print()

print("============================================================")