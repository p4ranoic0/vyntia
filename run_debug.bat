@echo off
cd /d d:\INTRANET\back
echo Starting debug script...
d:\INTRANET\.venv\Scripts\python.exe debug_500_errors.py 2>&1
echo.
echo Debug script completed. Press any key to continue...
pause
