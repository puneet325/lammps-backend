import os
import sys
import json
import subprocess


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

PYTHON = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")
OVITO_PYTHON = os.path.join(PROJECT_DIR, "ovito-env", "Scripts", "python.exe")

INPUT_DIR = os.path.join(PROJECT_DIR, "inputs")
REPORT_DIR = os.path.join(PROJECT_DIR, "reports")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")

PARAMETERS_FILE = os.path.join(INPUT_DIR, "parameters.json")

OVITO_IMAGE = os.path.join(
    REPORT_DIR,
    "ovito_deformation.png"
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def run_script(script, python_executable=PYTHON):
    """Run one project script and stop if it fails."""

    script_path = os.path.join(PROJECT_DIR, "src", script)

    print("\n" + "=" * 60)
    print(f"RUNNING: {script}")
    print("=" * 60)

    result = subprocess.run(
        [python_executable, script_path],
        cwd=PROJECT_DIR
    )

    if result.returncode != 0:
        print(f"\nERROR: {script} failed.")
        print(f"Return code: {result.returncode}")
        sys.exit(result.returncode)

    print(f"\n{script} completed successfully.")


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# PROJECT HEADER
# ============================================================

print("\n")
print("=" * 60)
print("        LAMMPS AUTOMATION PROJECT")
print("=" * 60)
print()
print("Complete automated simulation and analysis pipeline")
print()
print("Pipeline:")
print("Input parameters")
print("      -> LAMMPS simulation")
print("      -> Elastic-property analysis")
print("      -> OVITO trajectory analysis")
print("      -> DOE / parameter sweep")
print("      -> ML surrogate")
print("      -> Human feedback")
print("      -> Multiscale material properties")
print("      -> Experimental comparison")
print("      -> Project validation")
print()


# ============================================================
# ASK USER FOR SIMULATION PARAMETERS
# ============================================================

print("=" * 60)
print("ENTER SIMULATION PARAMETERS")
print("=" * 60)

material = input("Material [silicon]: ").strip()

if material == "":
    material = "silicon"

temperature_input = input("Temperature in K [300]: ").strip()

if temperature_input == "":
    temperature = 300
else:
    temperature = float(temperature_input)


deformation_input = input("Deformation [0.02]: ").strip()

if deformation_input == "":
    deformation = 0.02
else:
    deformation = float(deformation_input)


strain_rate_input = input("Strain rate [0.001]: ").strip()

if strain_rate_input == "":
    strain_rate = 0.001
else:
    strain_rate = float(strain_rate_input)


# ============================================================
# SAVE PARAMETERS
# ============================================================

parameters = {
    "materials": material,
    "temperature": temperature,
    "deformation": deformation,
    "strain_rate": strain_rate
}

with open(PARAMETERS_FILE, "w") as f:
    json.dump(parameters, f, indent=4)

print("\nParameters saved to:")
print(PARAMETERS_FILE)

print("\nSelected parameters:")
print(f"Material      : {material}")
print(f"Temperature   : {temperature} K")
print(f"Deformation   : {deformation}")
print(f"Strain rate   : {strain_rate}")

print("\nNOTE:")
print("The current LAMMPS elastic example uses temperature")
print("and deformation. The strain_rate value is stored for")
print("the pipeline interface but is not used by the current")
print("elastic input script.")


# ============================================================
# 1. GENERATE LAMMPS INPUT
# ============================================================

run_script("generate_inputs.py")


# ============================================================
# 2. RUN LAMMPS SIMULATION
# ============================================================

run_script("run_simulation.py")


# ============================================================
# 3. ANALYZE LAMMPS RESULTS
# ============================================================

run_script("analyze_results.py")


# ============================================================
# 4. OVITO ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("RUNNING: OVITO VISUALIZATION + DEFORMATION ANALYSIS")
print("=" * 60)

visualize_script = os.path.join(
    PROJECT_DIR,
    "src",
    "Visualize.py"
)

result = subprocess.run(
    [OVITO_PYTHON, visualize_script],
    cwd=PROJECT_DIR
)

if result.returncode != 0:
    print("\nERROR: OVITO analysis failed.")
    print(f"Return code: {result.returncode}")
    sys.exit(result.returncode)

print("\nOVITO analysis completed successfully.")

print("\nOVITO outputs:")

deformation_csv = os.path.join(
    RESULTS_DIR,
    "deformation_results.csv"
)

visualization_summary = os.path.join(
    REPORT_DIR,
    "visualization_summary.txt"
)

if os.path.exists(OVITO_IMAGE):
    print(f"Visualization : {OVITO_IMAGE}")

if os.path.exists(deformation_csv):
    print(f"Data          : {deformation_csv}")

if os.path.exists(visualization_summary):
    print(f"Summary       : {visualization_summary}")


# ============================================================
# 5. PARAMETER SWEEP / DOE
# ============================================================

run_script("doe_sweep.py")


# ============================================================
# 6. ML PIPELINE
# ============================================================

run_script("ml_pipeline.py")


# ============================================================
# 7. HUMAN FEEDBACK
# ============================================================

run_script("human_feedback.py")


# ============================================================
# 8. MULTISCALE BRIDGE
# ============================================================

run_script("multiscale_bridge.py")


# ============================================================
# 9. FEM MATERIAL CARD
# ============================================================

run_script("make_fem_material_card.py")


# ============================================================
# 10. EXPERIMENTAL COMPARISON
# ============================================================

run_script("compare_experiment.py")


# ============================================================
# 11. PROJECT VALIDATION
# ============================================================

run_script("validate_project.py")


# ============================================================
# OPEN OVITO VISUALIZATION
# ============================================================

print("\n" + "=" * 60)
print("OVITO VISUALIZATION")
print("=" * 60)

if os.path.exists(OVITO_IMAGE):

    print("\nOVITO visualization generated successfully.")
    print(f"\nOpening:")
    print(OVITO_IMAGE)

    try:
        os.startfile(OVITO_IMAGE)
        print("\nVisualization opened in the default Windows image viewer.")

    except Exception as e:
        print("\nCould not automatically open the image.")
        print(f"Reason: {e}")
        print(f"\nYou can manually open:")
        print(OVITO_IMAGE)

else:

    print("\nOVITO visualization image was not found.")
    print(f"Expected location:")
    print(OVITO_IMAGE)


# ============================================================
# FINAL OUTPUT SUMMARY
# ============================================================

print("\n")
print("=" * 60)
print("              PIPELINE COMPLETE")
print("=" * 60)

print("\nMAIN OUTPUTS:")

print("\n1. LAMMPS simulation")
print("   simulations/run_001/")

print("\n2. Elastic properties")
print("   results/properties.csv")

print("\n3. OVITO deformation data")
print("   results/deformation_results.csv")

print("\n4. OVITO visualization")
print("   reports/ovito_deformation.png")

print("\n5. OVITO summary")
print("   reports/visualization_summary.txt")

print("\n6. DOE results")
print("   results/doe_dataset.csv")

print("\n7. ML results")
print("   results/ml_results.csv")

print("\n8. Human feedback")
print("   results/expert_feedback.csv")

print("\n9. Multiscale properties")
print("   results/multiscale_material_properties.csv")

print("\n10. FEM material card")
print("    results/fem_material_card.json")

print("\n11. Experimental comparison")
print("    results/")

print("\n" + "=" * 60)
print("PROJECT PIPELINE FINISHED")
print("=" * 60)

print("\nImportant project status:")
print("- LAMMPS simulation: completed")
print("- Elastic analysis: completed")
print("- OVITO visualization: completed")
print("- Atomic displacement analysis: completed")
print("- DOE framework: available")
print("- ML surrogate: available")
print("- Human-feedback framework: available")
print("- Multiscale bridge: available")
print("- HPC SLURM workflow: prepared")
print("- Real experimental calibration: requires experimental data")
print("- 300-point HPC execution: requires an actual SLURM cluster")

print("\nThe OVITO visualization should now be open on your screen.")
print()