@echo off
rem Mo Blender 5.1, addon MCP tu bat server (cong 9876)
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py start blender
if errorlevel 1 (pause) else (timeout /t 4 >nul)
