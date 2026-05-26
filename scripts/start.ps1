# BulkPing - start all services (requires Docker Desktop running)
$ErrorActionPreference = "Stop"
$docker = "${env:ProgramFiles}\Docker\Docker\resources\bin\docker.exe"
if (-not (Test-Path $docker)) {
    $docker = "docker"
}

Write-Host "Checking Docker..."
& $docker version
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Docker engine is not ready. Please:"
    Write-Host "  1. Open Docker Desktop from the Start menu"
    Write-Host "  2. Wait until it says 'Docker Desktop is running'"
    Write-Host "  3. Complete WSL2 setup if prompted (may require a reboot)"
    Write-Host "  4. Run this script again: .\scripts\start.ps1"
    exit 1
}

Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

Write-Host "Building and starting BulkPing (first run may take 10-15 minutes)..."
& $docker compose up --build -d

Write-Host ""
Write-Host "Waiting for services..."
Start-Sleep -Seconds 20

Write-Host "Health check:"
try {
    Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "  API gateway: OK"
} catch {
    Write-Host "  API gateway: not ready yet (check: docker compose logs)"
}

Write-Host ""
Write-Host "URLs:"
Write-Host "  API:       http://localhost:8000/health"
Write-Host "  Streamlit: http://localhost:8501"
Write-Host "  Evolution: http://localhost:8080"
Write-Host ""
Write-Host "Logs: docker compose logs -f"
Write-Host "Stop: docker compose down"
