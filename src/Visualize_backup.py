import os
import csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ovito.io import import_file
from ovito.modifiers import (
    CalculateDisplacementsModifier,
    ColorCodingModifier
)
from ovito.vis import Viewport


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DUMP_FILE = os.path.join(
    BASE_DIR,
    "simulations",
    "run_001",
    "dump.lammpstrj"
)

RESULTS_DIR = os.path.join(BASE_DIR, "results")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

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

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


# ============================================================
# CHECK DUMP FILE
# ============================================================

print("========================================")
print("      OVITO DEFORMATION ANALYSIS")
print("========================================")
print()

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

pipeline = import_file(DUMP_FILE)

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
# COLOR ATOMS BY DISPLACEMENT
# ============================================================

print("Applying displacement coloring...")

color_modifier = ColorCodingModifier(
    property="Displacement Magnitude"
)

pipeline.modifiers.append(
    color_modifier
)


# ============================================================
# FINAL FRAME
# ============================================================

final_frame = num_frames - 1

data = pipeline.compute(final_frame)

particles = data.particles

num_atoms = particles.count

print("Atoms:", num_atoms)
print("Final frame:", final_frame)
print()


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
# CALCULATE STATISTICS
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

# Additional scale values
q25 = float(
    np.percentile(displacement_values, 25)
)

q50 = float(
    np.percentile(displacement_values, 50)
)

q75 = float(
    np.percentile(displacement_values, 75)
)


print("Atomic displacement analysis completed.")
print()

print(f"Mean displacement    : {mean_disp:.6f}")
print(f"Maximum displacement : {max_disp:.6f}")
print(f"Minimum displacement : {min_disp:.6f}")
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
# ADD PIPELINE TO SCENE
# ============================================================

pipeline.add_to_scene()


# ============================================================
# CREATE VIEWPORT
# ============================================================

viewport = Viewport(
    type=Viewport.Type.PERSPECTIVE,
    camera_dir=(1, 1, 1)
)

viewport.zoom_all()


# ============================================================
# RENDER ORIGINAL OVITO IMAGE
# ============================================================

print("Rendering OVITO visualization...")

viewport.render_image(
    filename=IMAGE_FILE,
    size=(1400, 1000),
    frame=final_frame,
    background=(1, 1, 1)
)


pipeline.remove_from_scene()

print("Base visualization rendered.")
print()


# ============================================================
# ADD DATA BOX + DISPLACEMENT SCALE
# ============================================================

print("Adding analysis data to image...")


image = Image.open(IMAGE_FILE).convert("RGB")

draw = ImageDraw.Draw(image)


# ------------------------------------------------------------
# FONT
# ------------------------------------------------------------

try:

    font_title = ImageFont.truetype(
        "arial.ttf",
        28
    )

    font_data = ImageFont.truetype(
        "arial.ttf",
        22
    )

except:

    font_title = ImageFont.load_default()
    font_data = ImageFont.load_default()


# ============================================================
# DATA BOX
# ============================================================

box_x = 35
box_y = 35

box_width = 390
box_height = 250

draw.rectangle(
    [
        box_x,
        box_y,
        box_x + box_width,
        box_y + box_height
    ],
    fill="white",
    outline="black",
    width=3
)


draw.text(
    (
        box_x + 20,
        box_y + 15
    ),
    "OVITO DEFORMATION ANALYSIS",
    fill="black",
    font=font_title
)


data_lines = [
    f"Atoms              : {num_atoms}",
    f"Frames             : {num_frames}",
    f"Final Frame        : {final_frame}",
    "",
    f"Mean Displacement  : {mean_disp:.6f}",
    f"Minimum            : {min_disp:.6f}",
    f"Maximum            : {max_disp:.6f}"
]


text_y = box_y + 65

for line in data_lines:

    draw.text(
        (
            box_x + 20,
            text_y
        ),
        line,
        fill="black",
        font=font_data
    )

    text_y += 27


# ============================================================
# DISPLACEMENT SCALE
# ============================================================

scale_x = 1280
scale_y = 250

scale_width = 45
scale_height = 420


# Create vertical blue -> cyan -> green -> yellow -> red scale
for i in range(scale_height):

    ratio = i / (scale_height - 1)

    # blue -> cyan -> green -> yellow -> red
    if ratio < 0.25:

        t = ratio / 0.25

        r = 0
        g = int(255 * t)
        b = int(255 * (1 - t))

    elif ratio < 0.50:

        t = (ratio - 0.25) / 0.25

        r = 0
        g = 255
        b = int(255 * (1 - t))

    elif ratio < 0.75:

        t = (ratio - 0.50) / 0.25

        r = int(255 * t)
        g = 255
        b = 0

    else:

        t = (ratio - 0.75) / 0.25

        r = 255
        g = int(255 * (1 - t))
        b = 0


    y = scale_y + i

    draw.line(
        [
            scale_x,
            y,
            scale_x + scale_width,
            y
        ],
        fill=(r, g, b),
        width=1
    )


# Border around scale

draw.rectangle(
    [
        scale_x,
        scale_y,
        scale_x + scale_width,
        scale_y + scale_height
    ],
    outline="black",
    width=2
)


# ============================================================
# SCALE LABEL
# ============================================================

draw.text(
    (
        scale_x - 120,
        scale_y - 40
    ),
    "Displacement",
    fill="black",
    font=font_data
)


# Maximum

draw.text(
    (
        scale_x + 55,
        scale_y - 5
    ),
    f"{max_disp:.3f}",
    fill="black",
    font=font_data
)


# 75%

draw.text(
    (
        scale_x + 55,
        scale_y + scale_height * 0.25 - 10
    ),
    f"{q75:.3f}",
    fill="black",
    font=font_data
)


# Median

draw.text(
    (
        scale_x + 55,
        scale_y + scale_height * 0.50 - 10
    ),
    f"{q50:.3f}",
    fill="black",
    font=font_data
)


# 25%

draw.text(
    (
        scale_x + 55,
        scale_y + scale_height * 0.75 - 10
    ),
    f"{q25:.3f}",
    fill="black",
    font=font_data
)


# Minimum

draw.text(
    (
        scale_x + 55,
        scale_y + scale_height - 15
    ),
    f"{min_disp:.3f}",
    fill="black",
    font=font_data
)


# ============================================================
# SAVE FINAL IMAGE
# ============================================================

image.save(
    IMAGE_FILE
)


print("Final visualization saved:")
print(IMAGE_FILE)
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
        f"Number of atoms: {num_atoms}\n"
    )

    file.write(
        f"Number of frames: {num_frames}\n"
    )

    file.write(
        f"Final frame: {final_frame}\n\n"
    )

    file.write(
        f"Minimum displacement: {min_disp:.6f}\n"
    )

    file.write(
        f"25% displacement: {q25:.6f}\n"
    )

    file.write(
        f"Median displacement: {q50:.6f}\n"
    )

    file.write(
        f"75% displacement: {q75:.6f}\n"
    )

    file.write(
        f"Mean displacement: {mean_disp:.6f}\n"
    )

    file.write(
        f"Maximum displacement: {max_disp:.6f}\n\n"
    )

    file.write(
        "The atoms are color-coded according "
        "to displacement magnitude.\n"
    )

    file.write(
        "The rendered image contains the "
        "numerical displacement statistics "
        "and displacement scale.\n"
    )


print("Summary saved:")
print(SUMMARY_FILE)
print()

print("========================================")
print("       OVITO ANALYSIS COMPLETE")
print("========================================")