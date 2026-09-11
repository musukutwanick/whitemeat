# Local development server for The White Meat Company site.
# Usage:  right-click > "Run with PowerShell"   OR   ./start_server.ps1
# Optional port:  ./start_server.ps1 -Port 8001

param([int]$Port = 8000)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

# --- 1. Ensure a virtual environment exists ---------------------------------
if (-not (Test-Path $venvPy)) {
    Write-Host "No .venv found - creating one..." -ForegroundColor Yellow
    $sysPy = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $sysPy -or $sysPy -match "WindowsApps") {
        $sysPy = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    }
    if (-not (Test-Path $sysPy)) {
        Write-Host "Python 3.12 not found. Install it first:  winget install Python.Python.3.12" -ForegroundColor Red
        exit 1
    }
    & $sysPy -m venv .venv
    & $venvPy -m pip install --upgrade pip
    & $venvPy -m pip install -r requirements.txt
}

# --- 2. Ensure a .env exists ----------------------------------------------
if (-not (Test-Path (Join-Path $PSScriptRoot ".env"))) {
    Write-Host "No .env found - copying from .env.example" -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# --- 3. Migrate + run ----------------------------------------------------
Write-Host "Applying migrations..." -ForegroundColor Green
& $venvPy manage.py migrate

Write-Host ""
Write-Host "Starting dev server on http://127.0.0.1:$Port/" -ForegroundColor Cyan
Write-Host "  Site      : http://127.0.0.1:$Port/" -ForegroundColor Cyan
Write-Host "  Django admin : http://127.0.0.1:$Port/admin/" -ForegroundColor Cyan
Write-Host "  Dashboard : http://127.0.0.1:$Port/login/" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""
& $venvPy manage.py runserver $Port
