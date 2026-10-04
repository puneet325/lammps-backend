import os
from datetime import datetime

import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

os.makedirs(REPORTS_DIR, exist_ok=True)


REPORT_FILE = os.path.join(
    REPORTS_DIR,
    "final_project_report.md"
)


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def load_csv(filename):

    path = os.path.join(
        RESULTS_DIR,
        filename
    )

    if os.path.exists(path):
        return pd.read_csv(path)

    return None


def format_value(value):

    if pd.isna(value):
        return "N/A"

    if isinstance(value, float):
        return f"{value:.4f}"

    return str(value)


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

simulation = load_csv(
    "doe_dataset.csv"
)

doe300 = load_csv(
    "doe_300_points.csv"
)

experiments = load_csv(
    "recommended_experiments.csv"
)

merged = load_csv(
    "merged_dataset.csv"
)

ml_results = load_csv(
    "ml_results.csv"
)

deformation = load_csv(
    "deformation_results.csv"
)

properties = load_csv(
    "properties.csv"
)


# ---------------------------------------------------------
# ML metrics
# ---------------------------------------------------------

mae = "N/A"
rmse = "N/A"
r2 = "N/A"

if ml_results is not None:

    for column in ml_results.columns:

        lower = column.lower()

        if "mae" in lower:
            mae = format_value(
                ml_results[column].iloc[0]
            )

        if "rmse" in lower:
            rmse = format_value(
                ml_results[column].iloc[0]
            )

        if lower == "r2":
            r2 = format_value(
                ml_results[column].iloc[0]
            )


# ---------------------------------------------------------
# Simulation summary
# ---------------------------------------------------------

simulation_count = (
    len(simulation)
    if simulation is not None
    else 0
)

doe_count = (
    len(doe300)
    if doe300 is not None
    else 0
)

experiment_count = (
    len(experiments)
    if experiments is not None
    else 0
)


# ---------------------------------------------------------
# Property summary
# ---------------------------------------------------------

property_text = ""

if properties is not None:

    property_text = f"""
### Reference elastic calculation

The current reference simulation produced:

| Property | Value |
|---|---:|
| C11 | {format_value(properties.loc[properties['Property'] == 'C11', 'Value'].iloc[0] if any(properties['Property'] == 'C11') else None)} |
| C12 | {format_value(properties.loc[properties['Property'] == 'C12', 'Value'].iloc[0] if any(properties['Property'] == 'C12') else None)} |
| C44 | {format_value(properties.loc[properties['Property'] == 'C44', 'Value'].iloc[0] if any(properties['Property'] == 'C44') else None)} |
| Bulk Modulus | {format_value(properties.loc[properties['Property'] == 'Bulk Modulus', 'Value'].iloc[0] if any(properties['Property'] == 'Bulk Modulus') else None)} |
| Poisson Ratio | {format_value(properties.loc[properties['Property'] == 'Poisson Ratio', 'Value'].iloc[0] if any(properties['Property'] == 'Poisson Ratio') else None)} |
"""


# ---------------------------------------------------------
# Experimental status
# ---------------------------------------------------------

experimental_status = (
    "No experimental measurements have been supplied yet."
)

if merged is not None:

    experimental_columns = [
        c for c in merged.columns
        if c.startswith("experimental_")
    ]

    if experimental_columns:

        if merged[experimental_columns].notna().any().any():

            experimental_status = (
                "Experimental measurements are present "
                "and can be compared with simulation results."
            )


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

date = datetime.now().strftime(
    "%Y-%m-%d %H:%M"
)


report = f"""# LAMMPS Automation and Multiscale Simulation Pipeline

**Generated:** {date}

---

## 1. Executive Summary

This project implements an automated atomistic simulation workflow based on LAMMPS.

The pipeline connects:

1. Parameter generation
2. LAMMPS simulation
3. Elastic-property extraction
4. OVITO trajectory/deformation analysis
5. Design of Experiments
6. Machine-learning surrogate modelling
7. Experimental-point selection
8. Human-feedback interface
9. Multiscale material-property export

The current prototype demonstrates the complete software architecture while keeping experimental measurements separate from simulation-generated data.

---

## 2. Overall Pipeline

```text
Input Parameters
       |
       v
Automatic Input Generation
       |
       v
LAMMPS Atomistic Simulation
       |
       +------------------+
       |                  |
       v                  v
Elastic Analysis        OVITO
       |                  |
       +--------+---------+
                |
                v
       Material Properties
                |
                v
        Design of Experiments
                |
                v
       300 Simulation Design
                |
          +-----+------+
          |            |
          v            v
      ML Model      Experiment
          |            |
          +-----+------+
                |
                v
       Simulation vs Experiment
                |
                v
         Human Feedback
                |
                v
        Parameter Adjustment
                |
                +------> New Simulation

Atomistic Properties
        |
        v
Mesoscale Parameters
        |
        v
Macroscale / Continuum Model"""