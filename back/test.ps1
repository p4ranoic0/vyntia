# Script de PowerShell para comandos de testing más directos
# Uso: .\test.ps1 [opción]
# Ejemplos: .\test.ps1, .\test.ps1 models, .\test.ps1 api, etc.

param(
    [string]$Command = "default"
)

# Colores para output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

# Variables
$TestDir = "tests/"
$Python = "python"
$Pytest = "python -m pytest"
$Manage = "python manage.py"

function Show-Help {
    Write-Host "${Yellow}🧪 Comandos de Testing Disponibles:${Reset}" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "${Green}Comandos Básicos:${Reset}" -ForegroundColor Green
    Write-Host "  .\test.ps1              - Tests con pytest (recomendado)"
    Write-Host "  .\test.ps1 simple       - Tests con Django (básico)"
    Write-Host "  .\test.ps1 verbose      - Tests detallados"
    Write-Host ""
    Write-Host "${Green}Tests Específicos:${Reset}" -ForegroundColor Green
    Write-Host "  .\test.ps1 models       - Solo tests de modelos"
    Write-Host "  .\test.ps1 api          - Solo tests de API"
    Write-Host "  .\test.ps1 auth         - Solo tests de autenticación"
    Write-Host "  .\test.ps1 usuario      - Solo tests de usuario"
    Write-Host "  .\test.ps1 area         - Solo tests de área"
    Write-Host "  .\test.ps1 fast         - Solo tests rápidos"
    Write-Host ""
    Write-Host "${Green}Reportes:${Reset}" -ForegroundColor Green
    Write-Host "  .\test.ps1 coverage     - Tests con cobertura"
    Write-Host "  .\test.ps1 html         - Tests con reporte HTML"
    Write-Host ""
    Write-Host "${Green}Utilidades:${Reset}" -ForegroundColor Green
    Write-Host "  .\test.ps1 clean        - Limpiar archivos temporales"
    Write-Host "  .\test.ps1 help         - Mostrar esta ayuda"
}

function Run-Command {
    param([string[]]$CmdArgs)
    
    $CmdString = $CmdArgs -join " "
    Write-Host "${Blue}🚀 Ejecutando: $CmdString${Reset}" -ForegroundColor Blue
    Write-Host ""
    
    & $CmdArgs[0] $CmdArgs[1..($CmdArgs.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "${Green}✅ Comando completado exitosamente!${Reset}" -ForegroundColor Green
    } else {
        Write-Host "${Red}❌ El comando falló con código de salida: $LASTEXITCODE${Reset}" -ForegroundColor Red
    }
    
    return $LASTEXITCODE
}

function Clean-TempFiles {
    Write-Host "${Green}🧹 Limpiando archivos temporales...${Reset}" -ForegroundColor Green
    
    # Eliminar directorios de cache
    if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }
    if (Test-Path ".pytest_cache") { Remove-Item ".pytest_cache" -Recurse -Force }
    if (Test-Path "htmlcov") { Remove-Item "htmlcov" -Recurse -Force }
    if (Test-Path "reports") { Remove-Item "reports" -Recurse -Force }
    if (Test-Path ".coverage") { Remove-Item ".coverage" -Force }
    
    # Buscar y eliminar archivos .pyc y directorios __pycache__
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | ForEach-Object {
        Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | ForEach-Object {
        Remove-Item $_ -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "${Green}✅ Limpieza completada!${Reset}" -ForegroundColor Green
}

# Procesar comando
switch ($Command.ToLower()) {
    "help" {
        Show-Help
        exit 0
    }
    
    "simple" {
        Write-Host "${Green}📋 Ejecutando tests con Django (salida simple)...${Reset}" -ForegroundColor Green
        Run-Command @($Python, "manage.py", "test", $TestDir, "--verbosity=1")
    }
    
    "verbose" {
        Write-Host "${Green}📋 Ejecutando tests detallados...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, $TestDir, "-v", "--tb=long", "--color=yes", "--durations=10", "--showlocals")
    }
    
    "models" {
        Write-Host "${Green}🏗️ Ejecutando tests de modelos...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, "tests/test_usuario_model.py", "tests/test_area_model.py", "-v", "--tb=short", "--color=yes")
    }
    
    "api" {
        Write-Host "${Green}🌐 Ejecutando tests de API...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, "tests/test_login_api.py", "-v", "--tb=short", "--color=yes")
    }
    
    "auth" {
        Write-Host "${Green}🔐 Ejecutando tests de autenticación...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, "tests/test_auth_system_integration.py", "-v", "--tb=short", "--color=yes")
    }
    
    "usuario" {
        Write-Host "${Green}👤 Ejecutando tests de usuario...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, "tests/test_usuario_model.py", "-v", "--tb=short", "--color=yes", "--durations=3")
    }
    
    "area" {
        Write-Host "${Green}🏢 Ejecutando tests de área...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, "tests/test_area_model.py", "-v", "--tb=short", "--color=yes", "--durations=3")
    }
    
    "fast" {
        Write-Host "${Green}⚡ Ejecutando tests rápidos...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, $TestDir, "-v", "--color=yes", "-m", "not slow", "--maxfail=3")
    }
    
    "coverage" {
        Write-Host "${Green}📊 Ejecutando tests con cobertura...${Reset}" -ForegroundColor Green
        $exitCode = Run-Command @($Pytest, $TestDir, "--cov=app_rrhh", "--cov-report=term-missing", "--cov-report=html:htmlcov", "-v", "--color=yes")
        if ($exitCode -eq 0) {
            Write-Host "${Yellow}📊 Reporte de cobertura generado en: htmlcov/index.html${Reset}" -ForegroundColor Yellow
        }
    }
    
    "html" {
        Write-Host "${Green}📄 Ejecutando tests con reporte HTML...${Reset}" -ForegroundColor Green
        if (!(Test-Path "reports")) { New-Item -ItemType Directory -Path "reports" }
        $exitCode = Run-Command @($Pytest, $TestDir, "--html=reports/test_report.html", "--self-contained-html", "-v", "--color=yes")
        if ($exitCode -eq 0) {
            Write-Host "${Yellow}📄 Reporte HTML generado en: reports/test_report.html${Reset}" -ForegroundColor Yellow
        }
    }
    
    "clean" {
        Clean-TempFiles
    }
    
    "default" {
        Write-Host "${Green}🚀 Ejecutando tests con pytest (configuración recomendada)...${Reset}" -ForegroundColor Green
        Run-Command @($Pytest, $TestDir, "-v", "--tb=short", "--color=yes", "--durations=3")
    }
    
    default {
        Write-Host "${Red}❓ Opción no reconocida: $Command${Reset}" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}

exit $LASTEXITCODE