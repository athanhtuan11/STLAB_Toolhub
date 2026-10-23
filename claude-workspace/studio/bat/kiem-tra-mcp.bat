@echo off
rem Kiem tra ca 4 MCP server: bat tay, lay danh sach tool, goi 1 tool chi doc vao app dang chay
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py status
echo.
uv run --no-project python launcher.py mcp-check all
pause
