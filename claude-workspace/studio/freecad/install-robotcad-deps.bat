@echo off
rem Cai thu vien Python cho RobotCAD bang Python cua FreeCAD 1.1, dung phien ban trong file lock.
rem Thu muc dich la noi RobotCAD tu them vao sys.path. --no-deps: khong keo them goi nao ngoai lock.
chcp 65001 >nul
set "FCPY=C:\Program Files\FreeCAD 1.1\bin\python.exe"
set "TARGET=%USERPROFILE%\.local\share\FreeCAD\AdditionalPythonPackages\py311"
"%FCPY%" -m pip install --disable-pip-version-check --no-warn-script-location --no-deps --target "%TARGET%" -r "%~dp0requirements-robotcad.lock.txt"
pause
