@echo off
rem STLAB Toolhub (Flask, cau hinh trong .flaskenv) tai http://127.0.0.1:5050 - dong cua so nay de tat
chcp 65001 >nul
cd /d "%~dp0.."
title STLAB Toolhub - dong cua so nay de tat giao dien
uv run --no-project python -c "import launcher,sys; sys.exit(0 if launcher.port_open(5050) else 1)"
if not errorlevel 1 (
  start "" http://127.0.0.1:5050
  exit /b 0
)
start "" /min powershell -NoProfile -Command "Start-Sleep 4; Start-Process 'http://127.0.0.1:5050'"
uv run flask run
pause
