# ==============================================================================
# AEGIS — Local Development Stack Startup Script (Windows PowerShell)
# Compliant with Section 5.4 & 21 of AEGIS Master Implementation Specification
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "        AEGIS — Adaptive Modular Cybersecurity Defense    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

# 1. Check or generate certificates
$certPath = Join-Path $root "infrastructure\certificates\gateway.pem"
if (-not (Test-Path $certPath)) {
    Write-Host "[*] Certificates not found. Generating development certificates..." -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "generate-certs.ps1")
} else {
    Write-Host "[+] Certificates verified in infrastructure/certificates/" -ForegroundColor Green
}

# 2. Check .env
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[*] Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $root ".env.example") $envFile
}

# 3. Check Docker status
Write-Host "[*] Verifying Docker Desktop..." -ForegroundColor Cyan
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Docker daemon is not running. Please start Docker Desktop and run this script again." -ForegroundColor Red
    Write-Host "[*] Falling back to local standalone mode via Python venv..." -ForegroundColor Yellow
    & .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
    exit 0
}

# 4. Build and start Compose stack
Write-Host "[*] Starting AEGIS Multi-Container Stack..." -ForegroundColor Cyan
docker compose -f compose.yaml up -d --build

Write-Host "`n[+] AEGIS Services started successfully!" -ForegroundColor Green
Write-Host "  - Command Deck Dashboard: http://127.0.0.1:8000/dashboard" -ForegroundColor White
Write-Host "  - REST API & Swagger UI:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  - Gateway Ingress (mTLS): https://127.0.0.1:8443" -ForegroundColor White
Write-Host "  - Gateway Stats:          http://127.0.0.1:8088/stats" -ForegroundColor White

