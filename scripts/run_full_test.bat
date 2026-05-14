@echo off
setlocal EnableDelayedExpansion

:: Unified script to start infrastructure and simulation on Windows
:: Usage: scripts\run_full_test.bat <player_id>

set PLAYER_ID=%1
if "%PLAYER_ID%"=="" (
    echo Usage: %0 ^<player_id^>
    exit /b 1
)

cd /d "%~dp0\.."

echo =======================================================
echo RUNNING FULL TEST - INFRA + SIMULATION
echo =======================================================

:: 1. Start Infrastructure
call scripts\run_local_test.bat

:: 2. Wait
echo Waiting 15 seconds for MySQL and Mongo (Replica Set) to initialize...
timeout /t 15 /nobreak > nul

:: 3. Start Simulation
call scripts\start_simulation.bat %PLAYER_ID%

endlocal
