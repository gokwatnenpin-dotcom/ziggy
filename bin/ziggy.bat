@echo off
setlocal enabledelayedexpansion
set REPO=%~dp0..
set PYTHON=python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 set PYTHON=py
if not defined ZIGGY_HOME set ZIGGY_HOME=%LOCALAPPDATA%\ziggy
if not defined ZIGGY_HOME set ZIGGY_HOME=%USERPROFILE%\.local\share\ziggy
set VENV=%ZIGGY_HOME%\venv
%PYTHON% --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo ziggy needs Python 3.9+. Install Python and try again.
  exit /b 1
)
set PYBIN=
if exist "%VENV%\Scripts\python.exe" (
  "%VENV%\Scripts\python.exe" -c "import rich,requests" >nul 2>nul
  if !ERRORLEVEL! equ 0 set PYBIN=%VENV%\Scripts\python.exe
)
if not defined PYBIN (
  echo Setting up ziggy for first use - one time only...
  if not exist "%ZIGGY_HOME%" mkdir "%ZIGGY_HOME%"
  %PYTHON% -m venv "%VENV%"
  if !ERRORLEVEL! neq 0 (
    echo Could not create venv.
    exit /b 1
  )
  "%VENV%\Scripts\python.exe" -m pip install --quiet --upgrade rich requests
  if !ERRORLEVEL! neq 0 (
    echo Could not install dependencies.
    exit /b 1
  )
  set PYBIN=%VENV%\Scripts\python.exe
)
set PYTHONPATH=%REPO%
"%PYBIN%" -m ziggy %*
exit /b %ERRORLEVEL%


