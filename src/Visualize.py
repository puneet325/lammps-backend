```python
import os
import csv

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from ovito.io import import_file
from ovito.modifiers import CalculateDisplacementsModifier


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
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
# FILE PATHS
# ============================================================

RUN_FOLDER = os.path.join(
    BASE_DIR,
    "simulations",
    RUN_ID
)

DUMP_FILE = os.path.join(
    RUN_FOLDER,
    "dump.lammpstrj"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

CSV_FILE = os.path.join(
    RESULTS_DIR,
    "deformation_results.csv"
)

IMAGE_FILE = os.path.join(
    REPORTS_DIR,
    "ovito_deformation.png"
)

SUMMARY_FILE = os.path.join(
    REPORTS_DIR,
    "visualization_summary.txt"
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    RESULTS_DIR,
    exist_ok=True
)

os.makedirs(
    REPORTS_DIR,
    exist_ok=True
)


# ============================================================
# START
# ============================================================

print("========================================")
print("      OVITO DEFORMATION ANALYSIS")
print("========================================")
print()

print("Run ID:", RUN_ID)
print("Simulation folder:", RUN_FOLDER)
print()


# ============================================================
# CHECK DUMP FILE
# ============================================================

if not os.path.exists(DUMP_FILE):

    print("ERROR: dump.lammpstrj not found:")
    print(DUMP_FILE)

    raise SystemExit(1)


print("Loading LAMMPS trajectory...")
print("File:", DUMP_FILE)
print()


# ============================================================
# LOAD TRAJECTORY
# ============================================================

pipeline = import_file(
    DUMP_FILE,
    multiple_frames=True
)

num_frames = pipeline.source.num_frames

print("Frames:", num_frames)
print()


# ============================================================
# DISPLACEMENT CALCULATION
# ============================================================

print("Calculating atomic displacement...")

displacement_modifier = CalculateDisplacementsModifier(
    reference_frame=0
)

pipeline.modifiers.append(
    displacement_modifier
)


# ============================================================
# FINAL FRAME
# ============================================================

final_frame = num_frames - 1

data = pipeline.compute(
    final_frame
)

particles = data.particles

num_atoms = particles.count

print("Atoms:", num_atoms)
print("Final frame:", final_frame)
print()


# ============================================================
# GET POSITIONS
# ============================================================

positions = np.asarray(
    particles["Position"]
)


# ============================================================
# GET DISPLACEMENT DATA
# ============================================================

displacement_property = particles[
    "Displacement Magnitude"
]

displacement_values = np.asarray(
    displacement_property
)


# ============================================================
# STATISTICS
# ============================================================

mean_disp = float(
    np.mean(displacement_values)
)

max_disp = float(
    np.max(displacement_values)
)

min_disp = float(
    np.min(displacement_values)
)

q25 = float(
    np.percentile(
        displacement_values,
        25
    )
)

q50 = float(
    np.percentile(
        displacement_values,
        50
    )
)

q75 = float(
    np.percentile(
        displacement_values,
        75
    )
)


print("Atomic displacement analysis completed.")
print()

print(
    f"Mean displacement    : {mean_disp:.6f}"
)

print(
    f"Maximum displacement : {max_disp:.6f}"
)

print(
    f"Minimum displacement : {min_disp:.6f}"
)

print()


# ============================================================
# SAVE CSV
# ============================================================

print("Saving displacement CSV...")

with open(
    CSV_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "Atom_ID",
            "Displacement_Magnitude"
        ]
    )

    for atom_id, value in enumerate(
        displacement_values,
        start=1
    ):

        writer.writerow(
            [
                atom_id,
                float(value)
            ]
        )


print("CSV saved:", CSV_FILE)
print()


# ============================================================
# HEADLESS 3D VISUALIZATION
# ============================================================

print("Generating headless 3D visualization...")

fig = plt.figure(
    figsize=(14, 10),
    dpi=100
)

ax = fig.add_subplot(
    111,
    projection="3d"
)

scatter = ax.scatter(
    positions[:, 0],
    positions[:, 1],
    positions[:, 2],
    c=displacement_values,
    cmap="viridis",
    s=18
)

ax.set_title(
    "OVITO Deformation Analysis",
    fontsize=18,
    pad=20
)

ax.set_xlabel(
    "X Position"
)

ax.set_ylabel(
    "Y Position"
)

ax.set_zlabel(
    "Z Position"
)

colorbar = fig.colorbar(
    scatter,
    ax=ax,
    pad=0.10,
    shrink=0.65
)

colorbar.set_label(
    "Displacement Magnitude"
)

ax.text2D(
    0.02,
    0.94,
    (
        f"Run ID: {RUN_ID}\n"
        f"Atoms: {num_atoms}\n"
        f"Frames: {num_frames}\n"
        f"Final Frame: {final_frame}\n\n"
        f"Mean: {mean_disp:.6f}\n"
        f"Minimum: {min_disp:.6f}\n"
        f"Maximum: {max_disp:.6f}"
    ),
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="top",
    bbox=dict(
        boxstyle="round",
        facecolor="white",
        alpha=0.9
    )
)

plt.tight_layout()

plt.savefig(
    IMAGE_FILE,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)

print("Visualization rendered successfully.")
print("Image:", IMAGE_FILE)
print()


# ============================================================
# SAVE SUMMARY
# ============================================================

with open(
    SUMMARY_FILE,
    "w"
) as file:

    file.write(
        "OVITO DEFORMATION ANALYSIS\n"
    )

    file.write(
        "===========================\n\n"
    )

    file.write(
        f"Run ID: {RUN_ID}\n"
    )

    file.write(
        f"Simulation folder: "
        f"{RUN_FOLDER}\n\n"
    )

    file.write(
        f"Number of atoms: "
        f"{num_atoms}\n"
    )

    file.write(
        f"Number of frames: "
        f"{num_frames}\n"
    )

    file.write(
        f"Final frame: "
        f"{final_frame}\n\n"
    )

    file.write(
        f"Minimum displacement: "
        f"{min_disp:.6f}\n"
    )

    file.write(
        f"25% displacement: "
        f"{q25:.6f}\n"
    )

    file.write(
        f"Median displacement: "
        f"{q50:.6f}\n"
    )

    file.write(
        f"75% displacement: "
        f"{q75:.6f}\n"
    )

    file.write(
        f"Mean displacement: "
        f"{mean_disp:.6f}\n"
    )

    file.write(
        f"Maximum displacement: "
        f"{max_disp:.6f}\n\n"
    )

    file.write(
        "The atoms are color-coded according "
        "to displacement magnitude.\n"
    )

    file.write(
        "The visualization is generated using "
        "headless Matplotlib rendering.\n"
    )


print("Summary saved:")
print(SUMMARY_FILE)
print()

print("========================================")
print("       OVITO ANALYSIS COMPLETE")
print("========================================")
```
