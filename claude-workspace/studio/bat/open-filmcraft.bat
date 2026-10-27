@echo off
rem Mo FilmCraft voi cong dieu khien 7920
chcp 65001 >nul
cd /d "%~dp0.."
uv run --no-project python launcher.py start filmcraft
if errorlevel 1 (pause) else (timeout /t 4 >nul)
