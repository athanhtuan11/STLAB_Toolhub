@echo off
rem Dua 4 MCP server (FreeCAD, Blender, LightCraft, PhotoCraft - ban da ghim) vao Claude Desktop.
rem Truoc khi chay: THOAT HAN Claude Desktop (khay he thong -> Quit). Ban cu duoc sao luu.
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py desktop-status
echo.
uv run --no-project python launcher.py desktop-sync
pause
