# ==============================================================================
# AEGIS — Local Development Stack Teardown Script (Windows PowerShell)
# ==============================================================================

param (
    [switch]$Volumes = $false
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

Write-Host "Stopping AEGIS Stack..." -ForegroundColor Cyan

if ($Volumes) {
    Write-Host "[!] Removing persistent volumes (destructive)..." -ForegroundColor Yellow
    docker compose -f compose.yaml down -v
} else {
    docker compose -f compose.yaml down
}

Write-Host "[+] AEGIS Services stopped cleanly." -ForegroundColor Green

