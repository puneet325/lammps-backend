@echo off

title LAMMPS Automation Pipeline

cd /d "%~dp0"

echo ============================================================
echo       LAMMPS AUTOMATION PROJECT
echo ============================================================
echo.
echo Starting complete pipeline...
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python virtual environment not found.
    echo.
    echo Expected:
    echo .venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" "run_project.py"

echo.
echo ============================================================
echo Pipeline finished.
echo ============================================================
pause