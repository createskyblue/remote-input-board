@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
  echo Virtual environment not found: .venv\Scripts\activate.bat
  echo Create it first, for example: uv venv
  exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m py_remote_input
