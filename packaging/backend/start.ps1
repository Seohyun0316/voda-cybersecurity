$ErrorActionPreference = "Stop"
$BackendRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$VenvPython = Join-Path $BackendRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw "The backend is not installed. Run install.cmd first."
}

$env:PYTHONDONTWRITEBYTECODE = "1"
Write-Host "[VibeSafe] Starting the local backend."
Write-Host "[VibeSafe] Health check: http://127.0.0.1:38457/health"
Write-Host "[VibeSafe] Press Ctrl+C to stop."

Push-Location $BackendRoot
try {
    & $VenvPython -B app.py
    if ($LASTEXITCODE -ne 0) {
        throw "The backend exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
