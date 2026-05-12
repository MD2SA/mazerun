@echo off
setlocal

:: Unified script to start infrastructure and immediately trigger a simulation on Windows
:: Usage: scripts\run_full_test.bat <player_id>

set PLAYER_ID=%1

if "%PLAYER_ID%"=="" (
    echo Usage: %0 ^<player_id^>
    exit /b 1
)

:: Ensure we are in the project root
cd %~dp0\..

:: 1. Start Infrastructure
call scripts\run_local_test.bat

:: 2. Wait for databases to be ready
echo Waiting 5 seconds for infrastructure to settle...
timeout /t 5 /nobreak > nul

:: 3. Start Simulation
call scripts\start_simulation.bat %PLAYER_ID%
