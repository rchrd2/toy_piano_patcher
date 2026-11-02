@echo off
rem Double-click in File Explorer to open the patcher window.
cd /d "%~dp0"

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
echo Python 3 was not found. Install it from https://www.python.org/downloads/
pause
exit /b 1

:finished
if not %errorlevel%==0 (
    echo.
    echo The patcher stopped with an error, code %errorlevel%.
    pause
)
