@echo off
rem Mo LightCraft voi cong dieu khien 7980
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py start lightcraft
if errorlevel 1 (pause) else (timeout /t 4 >nul)
