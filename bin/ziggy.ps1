#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO = Split-Path -Parent $scriptDir

$PYTHON = $null
try {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { $PYTHON = $cmd.Source }
} catch {}
if (-not $PYTHON) {
    try {
        $cmd = Get-Command py -ErrorAction SilentlyContinue
        if ($cmd) { $PYTHON = $cmd.Source }
    } catch {}
}
if (-not $PYTHON) {
    Write-Error "ziggy needs Python 3.9+. Install Python and try again."
    exit 1
}

$ZIGGY_HOME = $env:ZIGGY_HOME
if (-not $ZIGGY_HOME) {
    if ($env:LOCALAPPDATA) {
        $ZIGGY_HOME = Join-Path $env:LOCALAPPDATA "ziggy"
    } else {
        $ZIGGY_HOME = Join-Path $env:USERPROFILE ".local\share\ziggy"
    }
}
$VENV = Join-Path $ZIGGY_HOME "venv"
$venvPython = Join-Path $VENV "Scripts\python.exe"

$PYBIN = $null
if (Test-Path $venvPython) {
    try {
        & $venvPython -c "import rich,requests" 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { $PYBIN = $venvPython }
    } catch {}
}

if (-not $PYBIN) {
    Write-Host "Setting up ziggy for first use - one time only..."
    New-Item -ItemType Directory -Force -Path $ZIGGY_HOME | Out-Null
    & $PYTHON -m venv $VENV
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Could not create a virtual environment."
        exit 1
    }
    & $venvPython -m pip install --quiet --upgrade rich requests
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Could not install dependencies."
        exit 1
    }
    $PYBIN = $venvPython
}

$env:PYTHONPATH = $REPO
& $PYBIN -m ziggy @args
exit $LASTEXITCODE
