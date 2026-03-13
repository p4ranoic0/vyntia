@echo off
cd d:\INTRANET\back
python -m py_compile api/v1/rrhh/permissions.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Sintaxis OK - No hay errores
    python manage.py check
    echo.
) else (
    echo Error de sintaxis detectado
)
pause
