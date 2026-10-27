@echo off
rem Mo moi ung dung trong apps.json, kiem tra MCP, roi mo Claude Code
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py start all
echo.
uv run --no-project python launcher.py mcp-check all
echo.
uv run --no-project python launcher.py claude
pause
