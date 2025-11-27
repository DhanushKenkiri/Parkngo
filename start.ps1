# ParknGo Multi-Agent Parking System
# Production Startup Script

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🚀 ParknGo Multi-Agent Parking System - Startup" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "   ❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "   Please create .env file with required credentials" -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✅ Environment file: Found" -ForegroundColor Green

# Check if Firebase credentials exist
if (-not (Test-Path "secrets\parkngo-firebase-adminsdk.json")) {
    Write-Host "   ⚠️  Warning: Firebase credentials not found in secrets/" -ForegroundColor Yellow
    Write-Host "   Some features may not work without Firebase credentials" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Firebase credentials: Found" -ForegroundColor Green
}

Write-Host ""

# Check Masumi services
Write-Host "🐳 Checking Masumi Docker Services..." -ForegroundColor Yellow

$masumiRunning = docker ps --filter "name=masumi" --format "{{.Names}}" 2>$null

if ($masumiRunning) {
    $containerCount = ($masumiRunning | Measure-Object -Line).Lines
    Write-Host "   ✅ Masumi services running: $containerCount containers" -ForegroundColor Green
    
    # List running containers
    docker ps --filter "name=masumi" --format "table {{.Names}}\t{{.Status}}" | Out-String | ForEach-Object {
        $_.Split("`n") | Where-Object { $_ -match "masumi" } | ForEach-Object {
            Write-Host "      $_" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "   ⚠️  Masumi services not running" -ForegroundColor Yellow
    Write-Host "   Starting Masumi services..." -ForegroundColor Yellow
    
    Push-Location masumi
    docker compose up -d
    Pop-Location
    
    Start-Sleep -Seconds 3
    Write-Host "   ✅ Masumi services started" -ForegroundColor Green
}

Write-Host ""

# Install/check dependencies
Write-Host "📦 Checking Python Dependencies..." -ForegroundColor Yellow

$requiredPackages = @("flask", "flask-cors", "firebase-admin", "google-generativeai", "requests")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $installed = python -c "import $($package.Replace('-', '_'))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "   ⚠️  Missing packages: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "   Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ All dependencies installed" -ForegroundColor Green
}

Write-Host ""

# Display startup banner
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🤖 AI Agents Initialized:" -ForegroundColor Green
Write-Host "   ✅ Orchestrator Agent (master coordinator)" -ForegroundColor White
Write-Host "   ✅ SpotFinder Agent (Gemini AI ranking)" -ForegroundColor White
Write-Host "   ✅ PricingAgent (Gemini demand forecasting)" -ForegroundColor White
Write-Host "   ✅ RouteOptimizer Agent (Gemini directions)" -ForegroundColor White
Write-Host "   ✅ PaymentVerifier Agent (Gemini fraud detection)" -ForegroundColor White
Write-Host "   ✅ SecurityGuard Agent (Gemini anomaly detection)" -ForegroundColor White
Write-Host "   ✅ DisputeResolver Agent (Gemini AI arbitration)" -ForegroundColor White
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Start Flask API
Write-Host "🌐 Starting Flask API Server..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Run the app
python app.py
