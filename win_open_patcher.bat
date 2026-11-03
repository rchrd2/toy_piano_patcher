@echo off
rem Double-click in File Explorer to open the patcher window.
cd /d "%~dp0"

rem Use the Python bundled in vendor\ (see vendor\README.md), so nothing needs installing.
if exist "vendor\python-win\python.exe" (
    "vendor\python-win\python.exe" -B toy_piano_patcher.py
    goto finished
)
echo The bundled Python is missing, so looking for an installed Python.
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 -B toy_piano_patcher.py
    goto finished
)
where python >nul 2>&1
if %errorlevel%==0 (
    python -B toy_piano_patcher.py
    goto finished
)
echo Python 3 was not found. Download the patcher again, or install Python from https://www.python.org/downloads/
pause
exit /b 1

:finished
if not %errorlevel%==0 (
    echo.
    echo The patcher stopped with an error, code %errorlevel%.
    pause
)
