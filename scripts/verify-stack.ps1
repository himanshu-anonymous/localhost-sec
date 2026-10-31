# ==============================================================================
# AEGIS — Stack Health & Verification Script (Windows PowerShell)
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "Verifying AEGIS System Health & Endpoints..." -ForegroundColor Cyan

$pythonExe = Join-Path $PSScriptRoot "..\\.venv\\Scripts\\python.exe"
if (-not (Test-Path $pythonExe)) { $pythonExe = "python" }

# 1. Run complete pytest automated test suite
Write-Host "`n[*] Running automated test suite across all domains..." -ForegroundColor Cyan
& $pythonExe -m pytest (Join-Path $PSScriptRoot "..\\backend\\tests") -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[+] All 36 Automated Tests Passed Successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[!] Automated tests reported failures. Check logs above." -ForegroundColor Red
}

