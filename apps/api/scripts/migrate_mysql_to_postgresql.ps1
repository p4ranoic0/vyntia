Param(
    [string]$SourceSettings = "vyntia.settings.development",
    [string]$TargetSettings = "vyntia.settings.development",
    [string]$OutDir = "tmp"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot "..\.venv\Scripts\python.exe"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFile = Join-Path $projectRoot "$OutDir\mysql_export_$timestamp.json"

if (-not (Test-Path $pythonExe)) {
    throw "No se encontró Python del entorno virtual: $pythonExe"
}

if (-not (Test-Path (Split-Path -Parent $dumpFile))) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $dumpFile) | Out-Null
}

Write-Host "[1/3] Exportando datos desde origen ($SourceSettings)..."
$env:DJANGO_SETTINGS_MODULE = $SourceSettings
$dumpArgs = @(
    "dumpdata",
    "--natural-foreign",
    "--natural-primary",
    "--exclude", "contenttypes",
    "--exclude", "auth.permission",
    "--indent", "2",
    "-o", $dumpFile
)
& $pythonExe "$projectRoot\manage.py" @dumpArgs

Write-Host "[2/3] Aplicando migraciones en destino ($TargetSettings)..."
$env:DJANGO_SETTINGS_MODULE = $TargetSettings
$migrateArgs = @("migrate", "--noinput")
& $pythonExe "$projectRoot\manage.py" @migrateArgs

Write-Host "[3/3] Cargando datos en destino..."
$loadArgs = @("loaddata", $dumpFile)
& $pythonExe "$projectRoot\manage.py" @loadArgs

Write-Host "Migración completada. Archivo de respaldo: $dumpFile"
