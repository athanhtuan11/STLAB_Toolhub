@echo off
rem Mo FreeCAD 1.1 va bat RPC server cho MCP (cong 9875)
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py start freecad
if errorlevel 1 (pause) else (timeout /t 4 >nul)
