from pathlib import Path
import re
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DOE_FILE = ROOT / "results" / "doe_300_points.csv"
HPC_SIMULATIONS = ROOT / "hpc" / "project" / "simulations"
OUTPUT_FILE = ROOT / "results" / "hpc_300_results.csv"


print("=" * 60)
print("HPC RESULT COLLECTOR")
print("=" * 60)


# ---------------------------------------------------------
# 1. Check input file
# ---------------------------------------------------------

if not DOE_FILE.exists():
    print("ERROR: doe_300_points.csv not found.")
    print(DOE_FILE)
    raise SystemExit(1)


doe = pd.read_csv(DOE_FILE)

print(f"Planned DOE points: {len(doe)}")


# ---------------------------------------------------------
# 2. Function to extract values from LAMMPS log
# ---------------------------------------------------------

def extract_value(text, name):
    """
    Extract the last numerical value appearing after
    a specific LAMMPS property name.
    """

    pattern = rf"{re.escape(name)}\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"

    matches = re.findall(pattern, text)

    if not matches:
        return None

    return float(matches[-1])


# ---------------------------------------------------------
# 3. Parse one LAMMPS run
# ---------------------------------------------------------

def parse_run(run_dir):

    log_file = run_dir / "log.lammps"

    if not log_file.exists():
        return None

    try:
        text = log_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        return None


    # Check whether LAMMPS reported an error
    if "ERROR:" in text:

        return {
            "status": "FAILED"
        }


    values = {}

    properties = [
        "C11",
        "C22",
        "C33",
        "C12",
        "C13",
        "C23",
        "C44",
        "C55",
        "C66",
        "Bulk Modulus",
        "Poisson Ratio"
    ]


    for property_name in properties:

        values[property_name] = extract_value(
            text,
            property_name
        )


    # Determine whether useful properties were extracted
    if all(value is None for value in values.values()):

        return {
            "status": "FAILED"
        }


    return {
        "status": "SUCCESS",
        **values
    }


# ---------------------------------------------------------
# 4. Scan all 300 simulations
# ---------------------------------------------------------

results = []


for index, row in doe.iterrows():

    run_number = index + 1

    run_dir = (
        HPC_SIMULATIONS /
        f"run_{run_number}"
    )


    result = parse_run(run_dir)


    record = {
        "temperature": row["temperature"],
        "deformation": row["deformation"],
        "status": "NOT_RUN",
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
    }


    if result is not None:

        record["status"] = result["status"]

        if result["status"] == "SUCCESS":

            record["C11"] = result["C11"]
            record["C22"] = result["C22"]
            record["C33"] = result["C33"]
            record["C12"] = result["C12"]
            record["C13"] = result["C13"]
            record["C23"] = result["C23"]
            record["C44"] = result["C44"]
            record["C55"] = result["C55"]
            record["C66"] = result["C66"]

            record["Bulk_Modulus"] = (
                result["Bulk Modulus"]
            )

            record["Poisson_Ratio"] = (
                result["Poisson Ratio"]
            )


    results.append(record)


# ---------------------------------------------------------
# 5. Save collected results
# ---------------------------------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------

success_count = (
    results_df["status"] == "SUCCESS"
).sum()

failed_count = (
    results_df["status"] == "FAILED"
).sum()

not_run_count = (
    results_df["status"] == "NOT_RUN"
).sum()


print()
print("=" * 60)
print("HPC RESULT SUMMARY")
print("=" * 60)

print(f"SUCCESS  : {success_count}")
print(f"FAILED   : {failed_count}")
print(f"NOT RUN  : {not_run_count}")

print()
print(f"Output:")
print(OUTPUT_FILE)

print("=" * 60)