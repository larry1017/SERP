@echo off
cd /d %~dp0

if not exist .venv\Scripts\python.exe (
  echo Virtual environment not found. Create it first with:
  echo python -m venv .venv
  exit /b 1
)

call .venv\Scripts\activate.bat
set FLASK_APP=app.main
flask run
