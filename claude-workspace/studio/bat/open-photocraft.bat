@echo off
rem Mo PhotoCraft voi cong dieu khien 7981 (co token)
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py start photocraft
if errorlevel 1 (pause) else (timeout /t 4 >nul)
