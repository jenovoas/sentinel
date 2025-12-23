@echo off
REM Wrapper for Windows users - calls the PowerShell script
set SCRIPT_DIR=%~dp0
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-cpu-ollama.ps1" %*
