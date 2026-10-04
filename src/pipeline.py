import subprocess
import sys
import os
import json
from datetime import datetime


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


# ============================================================
# STATUS FILE
# ============================================================

RUN_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "simulations",
    RUN_ID
)

STATUS_FILE = os.path.join(
    RUN_FOLDER,
    "pipeline_status.json"
)


# ============================================================
# PYTHON
# ============================================================

PYTHON_EXECUTABLE = sys.executable


# ============================================================
# STATUS FUNCTION
# ============================================================

def update_status(progress, stage, message, status="running"):

    os.makedirs(RUN_FOLDER, exist_ok=True)

    data = {
        "status": status,
        "progress": progress,
        "stage": stage,
        "experiment_id": RUN_ID,
        "message": message,
        "updated_at": datetime.now().isoformat(timespec="seconds")
    }

    with open(
        STATUS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
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
pipeline_environment["LAMMPS_RUN_ID"] = RUN_ID


# ============================================================
# RUN FUNCTION
# ============================================================

def run_step(
    name,
    script,
    start_progress,
    start_stage,
    start_message
):

    update_status(
        start_progress,
        start_stage,
        start_message,
        "running"
    )

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

        update_status(
            start_progress,
            "FAILED",
            f"{name} failed with exit code {result.returncode}.",
            "failed"
        )

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
# INITIAL STATUS
# ============================================================

update_status(
    10,
    "INITIALIZING",
    "LAMMPS automation pipeline started.",
    "running"
)


# ============================================================
# STEP 1
# ============================================================

run_step(
    "STEP 1: GENERATING INPUT",
    "src/generate_inputs.py",
    20,
    "INPUT GENERATION",
    "Generating LAMMPS input files."
)


update_status(
    35,
    "INPUT READY",
    "LAMMPS input files generated successfully.",
    "running"
)


# ============================================================
# STEP 2
# ============================================================

run_step(
    "STEP 2: RUNNING LAMMPS SIMULATION",
    "src/run_simulation.py",
    45,
    "LAMMPS SIMULATION",
    "LAMMPS simulation is running."
)


update_status(
    60,
    "LAMMPS COMPLETE",
    "LAMMPS simulation completed successfully.",
    "running"
)


# ============================================================
# STEP 3
# ============================================================

run_step(
    "STEP 3: ANALYZING RESULTS",
    "src/analyze_results.py",
    70,
    "RESULT ANALYSIS",
    "Analyzing LAMMPS simulation results."
)


update_status(
    78,
    "ANALYSIS COMPLETE",
    "Elastic constants and material properties calculated.",
    "running"
)


# ============================================================
# STEP 4
# ============================================================

run_step(
    "STEP 4: OVITO VISUALIZATION",
    "src/Visualize.py",
    90,
    "OVITO VISUALIZATION",
    "Generating OVITO deformation analysis."
)


# ============================================================
# COMPLETE
# ============================================================

update_status(
    100,
    "COMPLETED",
    "LAMMPS automation completed successfully.",
    "completed"
)


print()
print("============================================================")
print("              PIPELINE COMPLETED SUCCESSFULLY")
print("============================================================")
print()
print("RUN ID:", RUN_ID)
print()