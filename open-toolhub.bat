@echo off
rem Nhap dup de mo giao dien STLAB Toolhub (http://127.0.0.1:5050).
rem Dong cua so den nay de tat giao dien.
chcp 65001 >nul
where uv >nul 2>nul
if errorlevel 1 (
  echo Khong tim thay "uv". Cai uv: https://docs.astral.sh/uv/
  pause
  exit /b 1
)
call "%~dp0claude-workspace\studio\bat\open-toolhub.bat"
