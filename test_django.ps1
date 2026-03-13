$ErrorActionPreference = 'Continue'

Write-Host "=== Testing Django Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Django check
Write-Host "1. Running Django check..." -ForegroundColor Yellow
cd d:\INTRANET\back
& d:\INTRANET\.venv\Scripts\python.exe manage.py check 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Django check PASSED" -ForegroundColor Green
}
else {
    Write-Host "❌ Django check FAILED" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== System Ready for Testing ===" -ForegroundColor Green
Write-Host "Run: python manage.py runserver 8000" -ForegroundColor Cyan
