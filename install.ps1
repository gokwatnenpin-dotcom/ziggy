#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$REPO_URL = if ($env:ZIGGY_REPO) { $env:ZIGGY_REPO } else { "https://github.com/OWNER/ziggy.git" }
$ZIGGY_HOME = if ($env:ZIGGY_HOME) { $env:ZIGGY_HOME } else { Join-Path $env:USERPROFILE ".local\share\ziggy" }
$SRC = Join-Path $ZIGGY_HOME "src"
$BIN_DIR = if ($env:ZIGGY_BIN_DIR) { $env:ZIGGY_BIN_DIR } else { Join-Path $env:USERPROFILE ".local\bin" }

$SELF_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
if ((Test-Path (Join-Path $SELF_DIR "pyproject.toml")) -and (Test-Path (Join-Path $SELF_DIR "ziggy"))) {
    $SRC = $SELF_DIR
} else {
    if (-not (Test-Path (Join-Path $SRC ".git"))) {
        Write-Host "Cloning ziggy into $SRC ..."
        New-Item -ItemType Directory -Force -Path $ZIGGY_HOME | Out-Null
        git clone --depth 1 $REPO_URL $SRC
    }
}

New-Item -ItemType Directory -Force -Path $BIN_DIR | Out-Null
$shimBat = Join-Path $BIN_DIR "ziggy.bat"
$shimContent = "@echo off" + [Environment]::NewLine + "`"$SRC\bin\ziggy.bat`" %*"
Set-Content -Path $shimBat -Value $shimContent -Encoding ASCII
Write-Host "Installed: $shimBat"

$pathList = $env:Path -split ";"
if ($pathList -notcontains $BIN_DIR) {
    Write-Host "Add $BIN_DIR to your PATH to run 'ziggy' from anywhere."
}

Write-Host ""
Write-Host "Done. Type 'ziggy' to start."
