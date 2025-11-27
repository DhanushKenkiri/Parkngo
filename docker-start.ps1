#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ParknGo Docker Deployment Script
.DESCRIPTION
    Stops existing Masumi containers and starts everything in Docker with proper Masumi integration
#>

Write-Host "ParknGo Docker Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Stop and remove existing Masumi containers in masumi folder
Write-Host "`nStopping existing Masumi containers..." -ForegroundColor Yellow
Push-Location masumi
docker compose down
Pop-Location
Write-Host "Existing Masumi containers stopped" -ForegroundColor Green

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host ".env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with required configuration" -ForegroundColor Yellow
    exit 1
}

# Check if Firebase credentials exist
if (!(Test-Path "secrets/parkngo-firebase-adminsdk.json")) {
    Write-Host "Firebase credentials not found!" -ForegroundColor Red
    Write-Host "Please add secrets/parkngo-firebase-adminsdk.json" -ForegroundColor Yellow
    exit 1
}

Write-Host "Configuration files verified" -ForegroundColor Green

# Build and start all services
Write-Host "`nBuilding and starting all services..." -ForegroundColor Yellow
Write-Host "This includes:" -ForegroundColor Cyan
Write-Host "  - ParknGo API Server (Flask + 7 AI Agents)" -ForegroundColor White
Write-Host "  - Masumi Payment Service" -ForegroundColor White
Write-Host "  - Masumi Registry Service" -ForegroundColor White
Write-Host "  - PostgreSQL (Payment DB)" -ForegroundColor White
Write-Host "  - PostgreSQL (Registry DB)" -ForegroundColor White
Write-Host ""

docker compose up -d --build

# Wait for services to be healthy
Write-Host "`nWaiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host "`nChecking service health..." -ForegroundColor Yellow

$services = @(
    @{Name="Masumi Payment Service"; URL="http://localhost:3001/api/v1/health"},
    @{Name="Masumi Registry Service"; URL="http://localhost:3000/api/v1/health"},
    @{Name="ParknGo API"; URL="http://localhost:5000/api/health"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "$($service.Name) is healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "$($service.Name) is starting... (may take a few moments)" -ForegroundColor Yellow
    }
}

# Show running containers
Write-Host "`nRunning containers:" -ForegroundColor Cyan
docker compose ps

Write-Host "`nParknGo is now running!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nServices:" -ForegroundColor Cyan
Write-Host "  ParknGo API:          http://localhost:5000" -ForegroundColor White
Write-Host "  Masumi Payment:       http://localhost:3001" -ForegroundColor White
Write-Host "  Masumi Registry:      http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "API Documentation:   See API_DOCUMENTATION.md" -ForegroundColor Cyan
Write-Host "Test API:            curl http://localhost:5000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop:             docker compose down" -ForegroundColor Yellow
Write-Host "View logs:           docker compose logs -f parkngo-api" -ForegroundColor Yellow
Write-Host ""
