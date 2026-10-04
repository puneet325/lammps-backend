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
# PYTHON EXECUTABLE
# ============================================================

# Uses the Python interpreter currently running this pipeline.
# Works locally and inside Docker/Render.
PYTHON_EXECUTABLE = sys.executable


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

pipeline_environment["LAMMPS_RUN_ID"] = RUN_ID


# ============================================================
# RUN FUNCTION
# ============================================================

def run_step(name, script):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)
    print()

    command = [
        PYTHON_EXECUTABLE,
        os.path.join(
            PROJECT_FOLDER,
            script
        )
    ]

    print("Python:", PYTHON_EXECUTABLE)
    print("Script:", script)
    print()

    result = subprocess.run(
        command,
        cwd=PROJECT_FOLDER,
        env=pipeline_environment,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print()
        print("=" * 60)
        print("STEP FAILED:", name)
        print("EXIT CODE:", result.returncode)
        print("=" * 60)
        print()

        raise SystemExit(result.returncode)

    print()
    print("=" * 60)
    print("STEP COMPLETED:", name)
    print("=" * 60)
    print()


# ============================================================
# PIPELINE
# ============================================================

run_step(
    "STEP 1: GENERATING INPUT",
    "src/generate_inputs.py"
)


run_step(
    "STEP 2: RUNNING LAMMPS SIMULATION",
    "src/run_simulation.py"
)


run_step(
    "STEP 3: ANALYZING RESULTS",
    "src/analyze_results.py"
)


run_step(
    "STEP 4: OVITO VISUALIZATION",
    "src/Visualize.py"
)


# ============================================================
# COMPLETE
# ============================================================

print()
print("============================================================")
print("              PIPELINE COMPLETED SUCCESSFULLY")
print("============================================================")
print()
print("RUN ID:", RUN_ID)
print()