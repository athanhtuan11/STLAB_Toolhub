@echo off
rem Bam dup: nap firmware do vao ESP32-A1S Audio Kit + mo log serial. Doi cong: flash.bat COM5
set PORT=%1
if "%PORT%"=="" set PORT=COM5
powershell -NoProfile -ExecutionPolicy Bypass -Command ". C:\Espressif\Initialize-Idf.ps1 -IdfId esp-idf-20ee62e792ea89630ac6a777ab3ebc57 *> $null; Set-Location '%~dp0'; idf.py -p %PORT% flash monitor"
pause
