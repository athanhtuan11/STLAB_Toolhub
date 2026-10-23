@echo off
rem Mo VS Code + Claude Code tai thu muc studio (dung studio/.mcp.json)
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py claude
if errorlevel 1 (pause) else (timeout /t 4 >nul)
