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

SWEEP_FILE = os.path.join(
    PROJECT_FOLDER,
    "inputs",
    "parameter_sweep.json"
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
    "simulation_dataset.csv"
)


# ============================================================
# FUNCTION 1
# REPLACE TEMPERATURE IN LAMMPS INPUT
# ============================================================

def replace_temperature(init_file, temperature):

    with open(init_file, "r") as file:
        data = file.read()

    pattern = r"variable\s+temp\s+equal\s+[0-9.eE+-]+"

    replacement = f"variable temp equal {temperature}"

    new_data, count = re.subn(
        pattern,
        replacement,
        data,
        count=1
    )

    if count != 1:
        raise RuntimeError(
            f"Could not find temperature variable in:\n{init_file}"
        )

    with open(init_file, "w") as file:
        file.write(new_data)


# ============================================================
# FUNCTION 2
# EXTRACT FINAL ELASTIC PROPERTIES FROM LAMMPS LOG
# ============================================================

def extract_properties(log_file):

    with open(
        log_file,
        "r",
        errors="ignore"
    ) as file:

        data = file.read()

    # IMPORTANT:
    # We specifically search for the FINAL printed values:
    #
    # Elastic Constant C11all = ...
    #
    # instead of intermediate "variable C11 equal ..."
    # lines.

    patterns = {

        "C11": (
            r"Elastic Constant C11all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C22": (
            r"Elastic Constant C22all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C33": (
            r"Elastic Constant C33all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C12": (
            r"Elastic Constant C12all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C13": (
            r"Elastic Constant C13all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C23": (
            r"Elastic Constant C23all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C44": (
            r"Elastic Constant C44all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C55": (
            r"Elastic Constant C55all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "C66": (
            r"Elastic Constant C66all\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "Bulk_Modulus": (
            r"Bulk Modulus\s*=\s*"
            r"([-+0-9.eE]+)"
        ),

        "Poisson_Ratio": (
            r"Poisson Ratio\s*=\s*"
            r"([-+0-9.eE]+)"
        )
    }

    properties = {}

    for name, pattern in patterns.items():

        matches = re.findall(
            pattern,
            data
        )

        if matches:

            # Use the final occurrence in the log.
            properties[name] = float(
                matches[-1]
            )

        else:

            properties[name] = None

    return properties


# ============================================================
# CHECK REQUIRED FILES/FOLDERS
# ============================================================

if not os.path.exists(
    LAMMPS_EXAMPLE_FOLDER
):

    raise FileNotFoundError(
        "LAMMPS example folder not found:\n"
        + LAMMPS_EXAMPLE_FOLDER
    )


if not os.path.exists(
    SWEEP_FILE
):

    raise FileNotFoundError(
        "Parameter sweep file not found:\n"
        + SWEEP_FILE
    )


os.makedirs(
    SIMULATIONS_FOLDER,
    exist_ok=True
)

os.makedirs(
    RESULTS_FOLDER,
    exist_ok=True
)


# ============================================================
# READ SWEEP PARAMETERS
# ============================================================

with open(
    SWEEP_FILE,
    "r"
) as file:

    sweep = json.load(file)


temperatures = sweep["temperature"]


# ============================================================
# START DATASET
# ============================================================

dataset = []


print()
print("=" * 60)
print("AUTOMATIC PARAMETER SWEEP")
print("=" * 60)

print()
print(
    f"Temperatures: {temperatures}"
)

print(
    f"Number of simulations: "
    f"{len(temperatures)}"
)


# ============================================================
# RUN EACH SIMULATION
# ============================================================

for index, temperature in enumerate(
    temperatures,
    start=1
):

    run_name = (
        f"run_{index:03d}"
    )

    run_folder = os.path.join(
        SIMULATIONS_FOLDER,
        run_name
    )

    print()
    print("-" * 60)

    print(
        f"SIMULATION "
        f"{index}/{len(temperatures)}"
    )

    print(
        f"Temperature: "
        f"{temperature} K"
    )

    print(
        f"Folder: "
        f"{run_name}"
    )

    print("-" * 60)


    # --------------------------------------------------------
    # Remove old run
    # --------------------------------------------------------

    if os.path.exists(
        run_folder
    ):

        shutil.rmtree(
            run_folder
        )


    # --------------------------------------------------------
    # Copy complete LAMMPS example
    # --------------------------------------------------------

    shutil.copytree(
        LAMMPS_EXAMPLE_FOLDER,
        run_folder
    )


    # --------------------------------------------------------
    # Locate init.mod
    # --------------------------------------------------------

    init_file = os.path.join(
        run_folder,
        "init.mod"
    )


    if not os.path.exists(
        init_file
    ):

        raise FileNotFoundError(
            "init.mod not found:\n"
            + init_file
        )


    # --------------------------------------------------------
    # Write temperature
    # --------------------------------------------------------

    replace_temperature(
        init_file,
        temperature
    )

    print(
        "Temperature parameter written."
    )


    # --------------------------------------------------------
    # Verify temperature
    # --------------------------------------------------------

    with open(
        init_file,
        "r"
    ) as file:

        init_data = file.read()


    expected_temperature = (
        f"variable temp equal {temperature}"
    )


    if expected_temperature not in init_data:

        raise RuntimeError(
            "Temperature verification failed "
            f"for {run_name}"
        )


    print(
        "Temperature verified:"
    )

    print(
        f"    {expected_temperature}"
    )


    # --------------------------------------------------------
    # Run LAMMPS
    # --------------------------------------------------------

    command = [
        "lmp",
        "-in",
        "in.elastic"
    ]


    result = subprocess.run(
        command,
        cwd=run_folder,
        capture_output=True,
        text=True
    )


    # --------------------------------------------------------
    # Check LAMMPS result
    # --------------------------------------------------------

    if result.returncode != 0:

        print()
        print(
            "LAMMPS FAILED"
        )

        print()
        print(
            "LAMMPS output:"
        )

        print(
            result.stdout[-2000:]
        )

        print()
        print(
            "LAMMPS error:"
        )

        print(
            result.stderr[-2000:]
        )


        dataset.append({

            "temperature": temperature,

            "status": "FAILED",

            "C11": None,
            "C22": None,
            "C33": None,
            "C12": None,
            "C13": None,
            "C23": None,
            "C44": None,
            "C55": None,
            "C66": None,

            "Bulk_Modulus": None,

            "Poisson_Ratio": None
        })

        continue


    print(
        "LAMMPS completed successfully."
    )


    # --------------------------------------------------------
    # Locate log file
    # --------------------------------------------------------

    log_file = os.path.join(
        run_folder,
        "log.lammps"
    )


    if not os.path.exists(
        log_file
    ):

        raise FileNotFoundError(
            "LAMMPS log file not found:\n"
            + log_file
        )


    # --------------------------------------------------------
    # Extract properties
    # --------------------------------------------------------

    properties = extract_properties(
        log_file
    )


    # --------------------------------------------------------
    # Verify extraction
    # --------------------------------------------------------

    missing_properties = [

        name

        for name, value
        in properties.items()

        if value is None
    ]


    if missing_properties:

        print()
        print(
            "WARNING:"
        )

        print(
            "Some properties "
            "could not be extracted:"
        )

        for name in missing_properties:

            print(
                f"    {name}"
            )


    # --------------------------------------------------------
    # Create dataset row
    # --------------------------------------------------------

    row = {

        "temperature": temperature,

        "status": "SUCCESS"
    }


    row.update(
        properties
    )


    dataset.append(
        row
    )


    # --------------------------------------------------------
    # Display important results
    # --------------------------------------------------------

    print()
    print(
        "Properties extracted:"
    )

    print(
        f"    C11 = "
        f"{properties['C11']}"
    )

    print(
        f"    C22 = "
        f"{properties['C22']}"
    )

    print(
        f"    C33 = "
        f"{properties['C33']}"
    )

    print(
        f"    C12 = "
        f"{properties['C12']}"
    )

    print(
        f"    C44 = "
        f"{properties['C44']}"
    )

    print(
        f"    Bulk Modulus = "
        f"{properties['Bulk_Modulus']}"
    )

    print(
        f"    Poisson Ratio = "
        f"{properties['Poisson_Ratio']}"
    )


# ============================================================
# SAVE DATASET
# ============================================================

fieldnames = [

    "temperature",

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

    for row in dataset:

        writer.writerow(
            row
        )


# ============================================================
# FINAL SUMMARY
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
print("=" * 60)
print("PARAMETER SWEEP COMPLETED")
print("=" * 60)

print()

print(
    f"Total simulations: "
    f"{len(dataset)}"
)

print(
    f"Successful simulations: "
    f"{successful}"
)

print(
    f"Failed simulations: "
    f"{failed}"
)

print()

print(
    "Dataset created:"
)

print(
    DATASET_FILE
)

print()
print(
    "Simulation folders:"
)

print(
    SIMULATIONS_FOLDER
)

print()
print(
    "=" * 60
)