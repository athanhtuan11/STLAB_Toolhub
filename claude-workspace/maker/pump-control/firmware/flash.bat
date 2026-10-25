@echo off
rem Bam dup: build + nap firmware may bom vao COM5 + mo monitor. Doi cong: flash.bat COM7
set PORT=%1
if "%PORT%"=="" set PORT=COM5
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0flash.ps1" -Port %PORT%
pause
