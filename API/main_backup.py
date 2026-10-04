from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import sys

app = FastAPI(title="LAMMPS Automation API")

# Allow your frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_DIR = Path(r"C:\Users\Dell\Desktop\lammps-automation")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "LAMMPS Automation API"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ready",
        "pipeline": "LAMMPS Automation"
    }


@app.post("/api/experiments")
def create_experiment(data: dict):
    return {
        "id": "EXP-001",
        "status": "created",
        "parameters": data
    }


@app.post("/api/experiments/{experiment_id}/run")
def run_experiment(experiment_id: str):

    process = subprocess.Popen(
        [sys.executable, str(PROJECT_DIR / "pipeline.py")],
        cwd=PROJECT_DIR
    )

    return {
        "id": experiment_id,
        "status": "running",
        "process_id": process.pid
    }