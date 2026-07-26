@echo off
rem ===========================================================================
rem  VYNTIA - lanzador de desarrollo
rem
rem    dev.cmd            levanta backend + frontend
rem    dev.cmd reload     reinicia ambos
rem    dev.cmd stop       detiene lo que este script levanto
rem    dev.cmd status     muestra que hay arriba
rem    dev.cmd logs       ultimas lineas   (anade -Follow para seguirlas)
rem    dev.cmd seed       carga los datos demo (seed_demo_pro)
rem
rem  Sin argumentos hace 'start' y espera una tecla al terminar, para que al
rem  abrirlo con doble clic la ventana no se cierre llevandose la salida.
rem  Define VYNTIA_DEV_NOPAUSE=1 para suprimir esa espera.
rem ===========================================================================
setlocal

set "SCRIPT=%~dp0scripts\dev.ps1"

rem Se prefiere PowerShell 7. La busqueda se hace con rutas absolutas y con el
rem operador %%~$PATH: en vez de where.exe, porque en entornos con el PATH
rem recortado (CI, sandboxes) where.exe puede no estar disponible y la deteccion
rem fallaria en silencio.
set "PS="
if exist "%ProgramFiles%\PowerShell\7\pwsh.exe" set "PS=%ProgramFiles%\PowerShell\7\pwsh.exe"
if not defined PS if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe" set "PS=%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe"
if not defined PS for %%I in (pwsh.exe) do if not "%%~$PATH:I"=="" set "PS=%%~$PATH:I"
if not defined PS if exist "%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not defined PS set "PS=powershell"

"%PS%" -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" %*
set "RC=%ERRORLEVEL%"

if not "%~1"=="" goto :fin
if defined VYNTIA_DEV_NOPAUSE goto :fin
pause

:fin
exit /b %RC%
