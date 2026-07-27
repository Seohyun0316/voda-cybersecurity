param(
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"
$BackendRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$VenvRoot = Join-Path $BackendRoot ".venv"
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "[VibeSafe] Creating a Python virtual environment..."
    & $PythonCommand -m venv $VenvRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the Python virtual environment."
    }
}

Write-Host "[VibeSafe] Installing backend dependencies..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to update pip."
}

& $VenvPython -m pip install --requirement (Join-Path $BackendRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install backend dependencies."
}

Push-Location $BackendRoot
try {
    & $VenvPython -B -c "from vibesafe.api import create_app; app = create_app(); assert app.test_client().get('/health').status_code == 200"
    if ($LASTEXITCODE -ne 0) {
        throw "The backend self-check failed."
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "[VibeSafe] Installation complete. Run start.cmd."
