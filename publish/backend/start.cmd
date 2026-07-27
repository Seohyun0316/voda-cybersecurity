@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 (
  echo.
  echo [VibeSafe] Backend startup failed.
  pause
  exit /b 1
)
