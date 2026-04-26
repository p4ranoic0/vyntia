@echo off
REM Script para generar tipos desde OpenAPI schema (Windows)
REM Uso: npm run generate:api

setlocal enabledelayedexpansion

set BACKEND_URL=http://localhost:8000
set SCHEMA_URL=%BACKEND_URL%/api/schema/

echo.
echo 🔄 Descargando OpenAPI schema desde: %SCHEMA_URL%
echo.

REM Alternative: usar curl si está disponible
powershell -Command "Invoke-WebRequest -Uri '%SCHEMA_URL%' -OutFile 'openapi-schema.json' -ErrorAction Stop" >nul 2>&1

if errorlevel 1 (
  echo ❌ Error al descargar schema. Verifica que el backend está corriendo en %BACKEND_URL%
  exit /b 1
)

echo ✅ Schema descargado
echo.
echo 🔨 Generando tipos...
echo.

REM Generar tipos
call npx openapi-typescript-codegen --config openapi.config.json

if errorlevel 1 (
  echo.
  echo ❌ Error al generar tipos
  exit /b 1
)

echo.
echo ✅ Tipos generados exitosamente en: src/generated/api/
echo.
echo 📝 Archivos generados:
echo    - models/ : Interfases para tipos de datos
echo    - services/ : Servicios para API calls
echo    - schemas/ : Esquemas JSON Schema
echo.
echo 💡 Próximo paso: Importar tipos en features
echo    import type { Empleado } from "@/generated/api/models"
echo.

del openapi-schema.json >nul 2>&1

endlocal
