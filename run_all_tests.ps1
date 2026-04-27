# Unified Testing Pipeline for Login Project

Write-Host "🚀 Starting Full Testing Pipeline..." -ForegroundColor Cyan

# 1. Backend Tests
Write-Host "`n[1/2] Running Backend Tests..." -ForegroundColor Yellow
$env:PYTHONPATH="."
Set-Location "backend"
& .\venv\Scripts\pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend tests failed. Aborting pipeline." -ForegroundColor Red
    Set-Location ".."
    exit $LASTEXITCODE
}
Set-Location ".."

# 2. Frontend E2E Tests
Write-Host "`n[2/2] Running Frontend E2E Tests..." -ForegroundColor Yellow
Set-Location "frontend"
$env:PYTHONPATH="."
& ..\backend\venv\Scripts\pytest e2e
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend E2E tests failed." -ForegroundColor Red
    Set-Location ".."
    exit $LASTEXITCODE
}
Set-Location ".."

Write-Host "`n✅ All tests passed successfully! Project is stable." -ForegroundColor Green
