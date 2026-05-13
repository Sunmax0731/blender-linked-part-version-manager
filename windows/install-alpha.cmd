@echo off
setlocal
set TARGET=%LOCALAPPDATA%\BlenderLinkedPartVersionManager
if "%1"=="--dry-run" (
  echo {"ok":true,"dryRun":true,"target":"%TARGET%"}
  exit /b 0
)
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js 20 or later is required.
  exit /b 1
)
if not exist "%TARGET%" mkdir "%TARGET%"
copy /Y "%~dp0blpvm-companion.mjs" "%TARGET%\blpvm-companion.mjs" >nul
copy /Y "%~dp0blpvm-companion.cmd" "%TARGET%\blpvm-companion.cmd" >nul
echo {"ok":true,"dryRun":false,"target":"%TARGET%"}
