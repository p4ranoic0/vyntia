@echo off
REM Script batch para comandos de testing más directos en Windows
REM Uso: test.bat [opción]
REM Ejemplos: test.bat, test.bat models, test.bat api, etc.

setlocal enabledelayedexpansion

set "TEST_DIR=tests/"
set "PYTHON=python"
set "PYTEST=python -m pytest"
set "MANAGE=python manage.py"

if "%1"=="" goto default
if "%1"=="help" goto help
if "%1"=="simple" goto simple
if "%1"=="verbose" goto verbose
if "%1"=="models" goto models
if "%1"=="api" goto api
if "%1"=="auth" goto auth
if "%1"=="usuario" goto usuario
if "%1"=="area" goto area
if "%1"=="fast" goto fast
if "%1"=="coverage" goto coverage
if "%1"=="html" goto html
if "%1"=="clean" goto clean

echo ❓ Opción no reconocida: %1
echo.
goto help

:help
echo 🧪 Comandos de Testing Disponibles:
echo.
echo Comandos Básicos:
echo   test.bat              - Tests con pytest (recomendado)
echo   test.bat simple       - Tests con Django (básico)
echo   test.bat verbose      - Tests detallados
echo.
echo Tests Específicos:
echo   test.bat models       - Solo tests de modelos
echo   test.bat api          - Solo tests de API
echo   test.bat auth         - Solo tests de autenticación
echo   test.bat usuario      - Solo tests de usuario
echo   test.bat area         - Solo tests de área
echo   test.bat fast         - Solo tests rápidos
echo.
echo Reportes:
echo   test.bat coverage     - Tests con cobertura
echo   test.bat html         - Tests con reporte HTML
echo.
echo Utilidades:
echo   test.bat clean        - Limpiar archivos temporales
echo   test.bat help         - Mostrar esta ayuda
goto end

:simple
echo 📋 Ejecutando tests con Django (salida simple)...
echo.
%PYTHON% manage.py test %TEST_DIR% --verbosity=1
goto end

:verbose
echo 📋 Ejecutando tests detallados...
echo.
%PYTEST% %TEST_DIR% -v --tb=long --color=yes --durations=10 --showlocals
goto end

:models
echo 🏗️ Ejecutando tests de modelos...
echo.
%PYTEST% tests/test_usuario_model.py tests/test_area_model.py -v --tb=short --color=yes
goto end

:api
echo 🌐 Ejecutando tests de API...
echo.
%PYTEST% tests/test_login_api.py -v --tb=short --color=yes
goto end

:auth
echo 🔐 Ejecutando tests de autenticación...
echo.
%PYTEST% tests/test_auth_system_integration.py -v --tb=short --color=yes
goto end

:usuario
echo 👤 Ejecutando tests de usuario...
echo.
%PYTEST% tests/test_usuario_model.py -v --tb=short --color=yes --durations=3
goto end

:area
echo 🏢 Ejecutando tests de área...
echo.
%PYTEST% tests/test_area_model.py -v --tb=short --color=yes --durations=3
goto end

:fast
echo ⚡ Ejecutando tests rápidos...
echo.
%PYTEST% %TEST_DIR% -v --color=yes -m "not slow" --maxfail=3
goto end

:coverage
echo 📊 Ejecutando tests con cobertura...
echo.
%PYTEST% %TEST_DIR% --cov=app_rrhh --cov-report=term-missing --cov-report=html:htmlcov -v --color=yes
if %errorlevel% equ 0 (
    echo.
    echo 📊 Reporte de cobertura generado en: htmlcov/index.html
)
goto end

:html
echo 📄 Ejecutando tests con reporte HTML...
echo.
if not exist "reports" mkdir reports
%PYTEST% %TEST_DIR% --html=reports/test_report.html --self-contained-html -v --color=yes
if %errorlevel% equ 0 (
    echo.
    echo 📄 Reporte HTML generado en: reports/test_report.html
)
goto end

:clean
echo 🧹 Limpiando archivos temporales...
echo.
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
if exist "htmlcov" rmdir /s /q "htmlcov"
if exist "reports" rmdir /s /q "reports"
if exist ".coverage" del ".coverage"

REM Limpiar archivos .pyc y directorios __pycache__ recursivamente
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"

echo ✅ Limpieza completada!
goto end

:default
echo 🚀 Ejecutando tests con pytest (configuración recomendada)...
echo.
%PYTEST% %TEST_DIR% -v --tb=short --color=yes --durations=3
goto end

:end
if %errorlevel% equ 0 (
    echo.
    echo ✅ Comando completado exitosamente!
) else (
    echo.
    echo ❌ El comando falló con código de salida: %errorlevel%
)

exit /b %errorlevel%