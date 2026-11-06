@echo off
REM Start ShopAssist AI FastAPI backend server for Windows

set DIR=%~dp0..
cd /d "%DIR%"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

set PYTHONPATH=%DIR%

echo Starting ShopAssist AI on http://localhost:8000...
"%PYTHON%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
