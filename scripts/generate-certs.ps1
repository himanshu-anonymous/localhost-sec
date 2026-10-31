# PowerShell script to generate AEGIS local development certificates
$ErrorActionPreference = "Stop"

Write-Host "Generating AEGIS Development mTLS Certificates..." -ForegroundColor Cyan

$scriptPath = Join-Path $PSScriptRoot "generate_certs.py"
$pythonPath = Join-Path $PSScriptRoot "..\\.venv\\Scripts\\python.exe"

if (-not (Test-Path $pythonPath)) {
    $pythonPath = "python"
}

& $pythonPath $scriptPath
Write-Host "Certificates ready in infrastructure/certificates/" -ForegroundColor Green

