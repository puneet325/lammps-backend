import json
import os
import shutil
import re
import csv
import subprocess


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_FOLDER = r"C:\Users\Dell\Desktop\lammps-automation"

LAMMPS_EXAMPLE_FOLDER = (
    r"C:\Users\Dell\Desktop\lammps"
    r"\examples\ELASTIC_T\DEFORMATION\Silicon"
)

CONFIG_FILE = os.path.join(
    PROJECT_FOLDER,
    "inputs",
    "doe_config.json"
)

SIMULATIONS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "simulations"
)

RESULTS_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "results"
)

DATASET_FILE = os.path.join(
    RESULTS_FOLDER,
    "doe_dataset.csv"
)


# ============================================================
# MODIFY LAMMPS PARAMETERS
# ============================================================

def modify_parameters(
    init_file,
    temperature,
    deformation
):

    with open(
        init_file,
        "r"
    ) as file:

        data = file.read()


    # Temperature

    data, temp_count = re.subn(
        r"variable\s+temp\s+equal\s+[0-9.eE+-]+",
        f"variable temp equal {temperature}",
        data,
        count=1
    )


    # Finite deformation

    data, deformation_count = re.subn(
        r"variable\s+up\s+equal\s+[0-9.eE+-]+",
        f"variable up equal {deformation}",
        data,
        count=1
    )


    if temp_count != 1:

        raise RuntimeError(
            "Temperature variable was not found."
        )


    if deformation_count != 1:

        raise RuntimeError(
            "Deformation variable was not found."
        )


    with open(
        init_file,
        "w"
    ) as file:

        file.write(data)


# ============================================================
# EXTRACT FINAL LAMMPS RESULTS
# ============================================================

def extract_properties(log_file):

    with open(
        log_file,
        "r",
        errors="ignore"
    ) as file:

        data = file.read()


    patterns = {

        "C11":
        r"Elastic Constant C11all\s*=\s*([-+0-9.eE]+)",

        "C22":
        r"Elastic Constant C22all\s*=\s*([-+0-9.eE]+)",

        "C33":
        r"Elastic Constant C33all\s*=\s*([-+0-9.eE]+)",

        "C12":
        r"Elastic Constant C12all\s*=\s*([-+0-9.eE]+)",

        "C13":
        r"Elastic Constant C13all\s*=\s*([-+0-9.eE]+)",

        "C23":
        r"Elastic Constant C23all\s*=\s*([-+0-9.eE]+)",

        "C44":
        r"Elastic Constant C44all\s*=\s*([-+0-9.eE]+)",

        "C55":
        r"Elastic Constant C55all\s*=\s*([-+0-9.eE]+)",

        "C66":
        r"Elastic Constant C66all\s*=\s*([-+0-9.eE]+)",

        "Bulk_Modulus":
        r"Bulk Modulus\s*=\s*([-+0-9.eE]+)",

        "Poisson_Ratio":
        r"Poisson Ratio\s*=\s*([-+0-9.eE]+)"
    }


    properties = {}


    for name, pattern in patterns.items():

        matches = re.findall(
            pattern,
            data
        )

        if matches:

            properties[name] = float(
                matches[-1]
            )

        else:

            properties[name] = None


    return properties


# ============================================================
# LOAD CONFIGURATION
# ============================================================

with open(
    CONFIG_FILE,
    "r"
) as file:

    config = json.load(file)


temperatures = config["temperature"]

deformations = config["deformation"]


# ============================================================
# CREATE OUTPUT FOLDERS
# ============================================================

os.makedirs(
    SIMULATIONS_FOLDER,
    exist_ok=True
)

os.makedirs(
    RESULTS_FOLDER,
    exist_ok=True
)


# ============================================================
# CREATE EXPERIMENT MATRIX
# ============================================================

experiments = []


for temperature in temperatures:

    for deformation in deformations:

        experiments.append(
            {
                "temperature": temperature,
                "deformation": deformation
            }
        )


print()
print("=" * 65)
print("MULTI-PARAMETER DESIGN OF EXPERIMENTS")
print("=" * 65)

print()

print(
    f"Temperatures: {temperatures}"
)

print(
    f"Deformations: {deformations}"
)

print()

print(
    f"Total simulation points: "
    f"{len(experiments)}"
)


# ============================================================
# RUN SIMULATIONS
# ============================================================

dataset = []


for index, experiment in enumerate(
    experiments,
    start=1
):

    temperature = experiment[
        "temperature"
    ]

    deformation = experiment[
        "deformation"
    ]


    run_name = (
        f"doe_{index:03d}"
    )


    run_folder = os.path.join(
        SIMULATIONS_FOLDER,
        run_name
    )


    print()
    print("-" * 65)

    print(
        f"SIMULATION "
        f"{index}/{len(experiments)}"
    )

    print(
        f"Temperature: "
        f"{temperature} K"
    )

    print(
        f"Deformation: "
        f"{deformation}"
    )

    print(
        f"Folder: "
        f"{run_name}"
    )

    print("-" * 65)


    # Remove previous run

    if os.path.exists(
        run_folder
    ):

        shutil.rmtree(
            run_folder
        )


    # Copy full LAMMPS example

    shutil.copytree(
        LAMMPS_EXAMPLE_FOLDER,
        run_folder
    )


    init_file = os.path.join(
        run_folder,
        "init.mod"
    )


    # Modify both parameters

    modify_parameters(
        init_file,
        temperature,
        deformation
    )


    print(
        "Parameters written."
    )


    # Verify

    with open(
        init_file,
        "r"
    ) as file:

        init_data = file.read()


    expected_temp = (
        f"variable temp equal {temperature}"
    )

    expected_deformation = (
        f"variable up equal {deformation}"
    )


    if expected_temp not in init_data:

        raise RuntimeError(
            "Temperature verification failed."
        )


    if expected_deformation not in init_data:

        raise RuntimeError(
            "Deformation verification failed."
        )


    print(
        "Parameters verified."
    )


    # Run LAMMPS

    result = subprocess.run(
        [
            "lmp",
            "-in",
            "in.elastic"
        ],
        cwd=run_folder,
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        print(
            "LAMMPS FAILED."
        )

        dataset.append(
            {
                "temperature": temperature,
                "deformation": deformation,
                "status": "FAILED"
            }
        )

        continue


    print(
        "LAMMPS completed successfully."
    )


    log_file = os.path.join(
        run_folder,
        "log.lammps"
    )


    properties = extract_properties(
        log_file
    )


    row = {

        "temperature": temperature,

        "deformation": deformation,

        "status": "SUCCESS"
    }


    row.update(
        properties
    )


    dataset.append(
        row
    )


    print(
        f"C11 = {properties['C11']}"
    )

    print(
        f"Bulk Modulus = "
        f"{properties['Bulk_Modulus']}"
    )

    print(
        f"Poisson Ratio = "
        f"{properties['Poisson_Ratio']}"
    )


# ============================================================
# SAVE DATASET
# ============================================================

fieldnames = [

    "temperature",
    "deformation",
    "status",

    "C11",
    "C22",
    "C33",

    "C12",
    "C13",
    "C23",

    "C44",
    "C55",
    "C66",

    "Bulk_Modulus",
    "Poisson_Ratio"
]


with open(
    DATASET_FILE,
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        dataset
    )


# ============================================================
# SUMMARY
# ============================================================

successful = sum(
    row.get("status") == "SUCCESS"
    for row in dataset
)

failed = sum(
    row.get("status") == "FAILED"
    for row in dataset
)


print()
print("=" * 65)
print("DOE SIMULATION COMPLETED")
print("=" * 65)

print()

print(
    f"Total simulations: "
    f"{len(dataset)}"
)

print(
    f"Successful: "
    f"{successful}"
)

print(
    f"Failed: "
    f"{failed}"
)

print()

print(
    "Dataset:"
)

print(
    DATASET_FILE
)