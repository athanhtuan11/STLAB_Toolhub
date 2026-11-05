@echo off
rem Dung: flash.bat COM5   (nap xiaozhi vao A1S; se de len firmware dang co)
if "%~1"=="" (echo Dung: flash.bat COMx & exit /b 1)
set MSYSTEM=
set MSYSTEM_PREFIX=
set MSYSTEM_CHOST=
set MINGW_PREFIX=
set MSYS=
set CHERE_INVOKING=
set IDF_TOOLS_PATH=C:\Espressif\tools-v6.1
cd /d "%~dp0build-src"
powershell -NoProfile -ExecutionPolicy Bypass -Command ". 'C:\Espressif\frameworks\esp-idf-v6.1\export.ps1'; idf.py -p %1 flash monitor"
