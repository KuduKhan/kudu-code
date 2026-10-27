# Run in Windows PowerShell from the extracted source checkout.
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env with local-only preview enabled. Never expose this mode remotely.'
}
if (-not (Test-Path '.venv')) { python -m venv .venv }
& '.venv\Scripts\python.exe' -m pip install -r requirements-dev.txt
& '.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000
