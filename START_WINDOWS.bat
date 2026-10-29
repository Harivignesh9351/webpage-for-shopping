@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python is missing. Install Python 3.11 or newer from python.org.
    echo Select Add Python to PATH during installation.
    pause
    exit /b 1
  )
  set "SHOP_PYTHON=python"
) else (
  set "SHOP_PYTHON=py -3"
)
where npm >nul 2>nul
if errorlevel 1 (
  echo Node.js is missing. Install Node.js LTS from nodejs.org then run this file again.
  pause
  exit /b 1
)
if not exist "backend\.venv\Scripts\python.exe" (
  %SHOP_PYTHON% -m venv backend\.venv
  if errorlevel 1 goto failure
)
"backend\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 goto failure
pushd frontend
call npm ci --no-audit --no-fund
if errorlevel 1 (
  popd
  goto failure
)
popd
"backend\.venv\Scripts\python.exe" launch.py
if errorlevel 1 goto failure
exit /b 0
:failure
echo.
echo Setup or startup failed. Read the error above and README_TAMIL.md.
pause
exit /b 1
