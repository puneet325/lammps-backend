from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import csv
import json
import os
import shutil
import subprocess
import time
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SIMULATIONS_DIR = PROJECT_ROOT / "simulations"
INPUTS_DIR = PROJECT_ROOT / "inputs"
PARAMETERS_FILE = INPUTS_DIR / "parameters.json"
PIPELINE_FILE = PROJECT_ROOT / "src" / "pipeline.py"
PYTHON_EXE = Path(sys.executable)
SHARED_RESULTS_DIR = PROJECT_ROOT / "results"
SHARED_REPORTS_DIR = PROJECT_ROOT / "reports"

SIMULATIONS_DIR.mkdir(exist_ok=True)
INPUTS_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="LAMMPS Automation API",
    description="API for automated LAMMPS simulation, analysis and OVITO visualization.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExperimentRequest(BaseModel):
    material: str
    temperature: float
    deformation: float
    strain_rate: float


EXPERIMENT_PROCESSES: dict[str, dict] = {}


def get_next_run_id() -> str:
    numbers = []
    for folder in SIMULATIONS_DIR.iterdir():
        if folder.is_dir() and folder.name.startswith("run_"):
            try:
                numbers.append(int(folder.name.replace("run_", "")))
            except ValueError:
                pass
    return f"run_{max(numbers) + 1 if numbers else 1:03d}"


def run_folder(experiment_id: str) -> Path:
    folder = SIMULATIONS_DIR / experiment_id
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404, detail=f"Experiment {experiment_id} does not exist.")
    return folder


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_status(experiment_id: str, status: str, progress: int, stage: str, message: str) -> None:
    folder = SIMULATIONS_DIR / experiment_id
    save_json(
        folder / "status.json",
        {
            "status": status,
            "progress": progress,
            "stage": stage,
            "experiment_id": experiment_id,
            "message": message,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
    )


def snapshot_outputs(experiment_id: str) -> None:
    """Copy shared pipeline outputs into the experiment folder after completion.

    The existing scientific pipeline writes to results/ and reports/. We preserve
    that pipeline and snapshot its outputs so each experiment has its own record.
    """
    folder = run_folder(experiment_id)
    snapshot_results = folder / "results"
    snapshot_reports = folder / "reports"
    snapshot_results.mkdir(exist_ok=True)
    snapshot_reports.mkdir(exist_ok=True)

    result_files = [
        "properties.csv",
        "deformation_results.csv",
    ]
    report_files = [
        "visualization_summary.txt",
        "ovito_deformation.png",
        "elastic_constants.png",
        "stress_strain.png",
    ]

    for name in result_files:
        source = SHARED_RESULTS_DIR / name
        if source.exists():
            shutil.copy2(source, snapshot_results / name)

    for name in report_files:
        source = SHARED_REPORTS_DIR / name
        if source.exists():
            shutil.copy2(source, snapshot_reports / name)

    save_json(
        folder / "completed.json",
        {
            "experiment_id": experiment_id,
            "completed_at": datetime.now().isoformat(timespec="seconds"),
        },
    )


def read_properties(experiment_id: str) -> dict[str, float]:
    folder = run_folder(experiment_id)
    path = folder / "results" / "properties.csv"
    if not path.exists():
        path = SHARED_RESULTS_DIR / "properties.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Simulation property results are not available yet.")

    values: dict[str, float] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) < 2:
                continue
            key = row[0].strip()
            value = row[1].strip()
            try:
                values[key] = float(value)
            except (ValueError, TypeError):
                continue
    return values


def read_deformation(experiment_id: str) -> dict:
    folder = run_folder(experiment_id)
    summary_path = folder / "reports" / "visualization_summary.txt"
    if not summary_path.exists():
        summary_path = SHARED_REPORTS_DIR / "visualization_summary.txt"

    import re

    if summary_path.exists():
        text = summary_path.read_text(encoding="utf-8", errors="ignore")

        def number_after(*labels):
            for label in labels:
                match = re.search(
                    rf"{re.escape(label)}\s*[:=]\s*([-+]?\d+(?:\.\d+)?)",
                    text,
                    flags=re.IGNORECASE,
                )
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        pass
            return None

        return {
            "frame": number_after("Final Frame", "Frame"),
            "atom_count": number_after("Atoms", "Atom Count"),
            "mean_displacement": number_after("Mean Displacement"),
            "max_displacement": number_after("Maximum", "Max Displacement", "Maximum Displacement"),
            "min_displacement": number_after("Minimum", "Min Displacement", "Minimum Displacement"),
        }

    path = folder / "results" / "deformation_results.csv"
    if not path.exists():
        path = SHARED_RESULTS_DIR / "deformation_results.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="OVITO deformation results are not available yet.")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise HTTPException(status_code=404, detail="OVITO deformation results are empty.")

    row = rows[-1]
    normalized = {
        str(k).strip().lower().replace(" ", "_").replace("-", "_"): v
        for k, v in row.items()
        if k is not None
    }

    def find_number(*names):
        normalized_names = [n.lower().replace(" ", "_").replace("-", "_") for n in names]
        for name in normalized_names:
            if name in normalized:
                try:
                    return float(normalized[name])
                except (TypeError, ValueError):
                    pass
        for key, value in normalized.items():
            if value in (None, ""):
                continue
            if any(name in key for name in normalized_names):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass
        return None

    return {
        "frame": find_number("frame", "frames"),
        "atom_count": find_number("atom_count", "atoms", "particles"),
        "mean_displacement": find_number("mean_displacement"),
        "max_displacement": find_number("max_displacement", "maximum_displacement"),
        "min_displacement": find_number("min_displacement", "minimum_displacement"),
    }


def visualization_file(experiment_id: str) -> Path:
    folder = run_folder(experiment_id)
    path = folder / "reports" / "ovito_deformation.png"
    if path.exists():
        return path
    return SHARED_REPORTS_DIR / "ovito_deformation.png"


def get_parameters(experiment_id: str) -> dict:
    data = load_json(run_folder(experiment_id) / "parameters.json", {})
    return data or {}


@app.get("/")
def home():
    return {"message": "LAMMPS Automation API is running", "status": "online", "version": "2.0.0"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "LAMMPS Automation API is working"}


@app.post("/api/experiments")
def create_experiment(data: ExperimentRequest):
    material = data.material.strip().lower()
    if material != "silicon":
        raise HTTPException(status_code=400, detail="Currently only Silicon is connected to the LAMMPS simulation template.")
    if data.temperature <= 0:
        raise HTTPException(status_code=400, detail="Temperature must be greater than 0 K.")
    if data.deformation <= 0:
        raise HTTPException(status_code=400, detail="Deformation must be greater than 0.")
    if data.strain_rate <= 0:
        raise HTTPException(status_code=400, detail="Strain rate must be greater than 0.")

    run_id = get_next_run_id()
    folder = SIMULATIONS_DIR / run_id
    folder.mkdir(parents=True, exist_ok=True)

    parameters = {
        "materials": material,
        "temperature": data.temperature,
        "deformation": data.deformation,
        "strain_rate": data.strain_rate,
    }
    save_json(PARAMETERS_FILE, parameters)
    save_json(folder / "parameters.json", parameters)
    write_status(run_id, "created", 0, "READY", "Experiment created and ready to run.")

    return {"status": "created", "experiment_id": run_id, "parameters": parameters, "message": f"Experiment {run_id} created successfully."}


@app.get("/api/experiments")
def list_experiments():
    records = []
    folders = [p for p in SIMULATIONS_DIR.iterdir() if p.is_dir() and p.name.startswith("run_")]
    folders.sort(key=lambda p: p.name, reverse=True)

    for folder in folders:
        experiment_id = folder.name
        params = load_json(folder / "parameters.json", {}) or {}
        status_data = load_json(folder / "status.json", {}) or {}
        completed = (folder / "completed.json").exists()
        records.append({
            "experiment_id": experiment_id,
            "material": str(params.get("materials", "silicon")).title(),
            "temperature": params.get("temperature"),
            "deformation": params.get("deformation"),
            "strain_rate": params.get("strain_rate"),
            "status": "completed" if completed else status_data.get("status", "created"),
            "updated_at": status_data.get("updated_at"),
            "bulk_modulus": None,
            "shear_modulus": None,
            "poisson_ratio": None,
        })
        if completed:
            try:
                properties = read_properties(experiment_id)
                records[-1]["bulk_modulus"] = properties.get("Bulk Modulus")
                records[-1]["shear_modulus"] = properties.get("Shear Modulus 1")
                records[-1]["poisson_ratio"] = properties.get("Poisson Ratio")
            except HTTPException:
                pass
    return {"experiments": records}


@app.post("/api/experiments/{experiment_id}/run")
def run_experiment(experiment_id: str):
    folder = run_folder(experiment_id)
    if not PIPELINE_FILE.exists():
        raise HTTPException(status_code=500, detail="pipeline.py was not found.")
    # In Docker/Render, sys.executable points to the Python interpreter inside the container.

    existing = EXPERIMENT_PROCESSES.get(experiment_id)
    if existing and existing["process"].poll() is None:
        return {"status": "already_running", "experiment_id": experiment_id, "process_id": existing["process"].pid}

    env = os.environ.copy()
    env["LAMMPS_RUN_ID"] = experiment_id
    try:
        process = subprocess.Popen([str(PYTHON_EXE), str(PIPELINE_FILE)], cwd=str(PROJECT_ROOT), env=env)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Failed to start LAMMPS pipeline: {error}")

    EXPERIMENT_PROCESSES[experiment_id] = {"process": process, "started_at": time.time()}
    write_status(experiment_id, "running", 10, "INITIALIZING EXPERIMENT", "LAMMPS automation has started.")
    return {"status": "started", "experiment_id": experiment_id, "process_id": process.pid}


@app.get("/api/experiments/{experiment_id}/status")
def experiment_status(experiment_id: str):
    folder = run_folder(experiment_id)
    process_info = EXPERIMENT_PROCESSES.get(experiment_id)
    process = process_info["process"] if process_info else None
    started_at = process_info["started_at"] if process_info else 0

    if folder.joinpath("completed.json").exists():
        return {"status": "completed", "progress": 100, "stage": "COMPLETED", "experiment_id": experiment_id, "message": "LAMMPS automation completed successfully."}

    if process is not None:
        return_code = process.poll()
        if return_code is not None:
            if return_code == 0:
                snapshot_outputs(experiment_id)
                write_status(experiment_id, "completed", 100, "COMPLETED", "LAMMPS automation completed successfully.")
                return {"status": "completed", "progress": 100, "stage": "COMPLETED", "experiment_id": experiment_id, "message": "LAMMPS automation completed successfully."}
            write_status(experiment_id, "failed", 100, "FAILED", f"LAMMPS pipeline exited with code {return_code}.")
            return {"status": "failed", "progress": 100, "stage": "FAILED", "experiment_id": experiment_id, "message": f"LAMMPS pipeline exited with code {return_code}."}

    def fresh(path: Path) -> bool:
        return path.exists() and (started_at == 0 or path.stat().st_mtime >= started_at)

    if fresh(SHARED_RESULTS_DIR / "deformation_results.csv"):
        progress, stage = 94, "OVITO ANALYSIS"
    elif fresh(SHARED_RESULTS_DIR / "properties.csv"):
        progress, stage = 78, "ANALYZING OUTPUT"
    elif fresh(folder / "dump.lammpstrj"):
        progress, stage = 60, "LAMMPS SIMULATION"
    elif fresh(folder / "log.lammps"):
        progress, stage = 45, "LAMMPS SIMULATION"
    elif fresh(folder / "in.elastic"):
        progress, stage = 20, "INITIALIZING EXPERIMENT"
    else:
        progress, stage = 10, "INITIALIZING EXPERIMENT"

    write_status(experiment_id, "running", progress, stage, f"{stage.title()} in progress.")
    return {"status": "running", "progress": progress, "stage": stage, "experiment_id": experiment_id, "message": f"{stage.title()} in progress."}


@app.get("/api/experiments/{experiment_id}/results")
def experiment_results(experiment_id: str):
    folder = run_folder(experiment_id)
    if not folder.joinpath("completed.json").exists():
        raise HTTPException(status_code=409, detail="Experiment has not completed yet.")

    return {
        "status": "completed",
        "experiment_id": experiment_id,
        "parameters": get_parameters(experiment_id),
        "properties": read_properties(experiment_id),
        "deformation": read_deformation(experiment_id),
        "visualization_url": f"/api/experiments/{experiment_id}/visualization",
    }


@app.get("/api/experiments/{experiment_id}/visualization")
def experiment_visualization(experiment_id: str):
    path = visualization_file(experiment_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="OVITO visualization is not available yet.")
    return FileResponse(path, media_type="image/png", filename=f"{experiment_id}_ovito_deformation.png")


@app.get("/api/experiments/{experiment_id}/report")
def experiment_report(experiment_id: str):
    folder = run_folder(experiment_id)
    if not folder.joinpath("completed.json").exists():
        raise HTTPException(status_code=409, detail="Experiment has not completed yet.")
    report = {
        "experiment_id": experiment_id,
        "parameters": get_parameters(experiment_id),
        "properties": read_properties(experiment_id),
        "deformation": read_deformation(experiment_id),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    return report


@app.get("/api/experiments/compare")
def compare_experiments(first: str, second: str):
    if first == second:
        raise HTTPException(status_code=400, detail="Choose two different experiments.")
    first_data = experiment_results(first)
    second_data = experiment_results(second)
    return {"first": first_data, "second": second_data}
