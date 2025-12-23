@echo off
REM Root-level wrapper for Windows that calls the scripts\start-cpu-ollama.bat
set SCRIPT_DIR=%~dp0scripts
if exist "%SCRIPT_DIR%\start-cpu-ollama.bat" (
  call "%SCRIPT_DIR%\start-cpu-ollama.bat" %*
) else (
  echo ⚠ helper script not found at %SCRIPT_DIR%\start-cpu-ollama.bat
)
