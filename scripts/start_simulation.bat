@echo off
setlocal EnableDelayedExpansion

set TEAM_ID=25
set PLAYER_ID=%1

if "%PLAYER_ID%"=="" (
    echo Usage: %0 ^<player_id^>
    exit /b 1
)

cd /d "%~dp0\.."

:: ====================== VENV ======================
set PYTHON_EXE=python
if exist "venv\Scripts\activate.bat" (
    echo [Launcher] Using root venv
    call venv\Scripts\activate.bat
) else if exist "mysql\persistence\venv\Scripts\activate.bat" (
    echo [Launcher] Using mysql\persistence venv
    call mysql\persistence\venv\Scripts\activate.bat
) else (
    echo [Launcher] No venv found. Creating one in root project...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ✘ ERROR: Failed to create virtual environment
        exit /b 1
    )
    echo [Launcher] venv created successfully. Activating...
    call venv\Scripts\activate.bat
)

echo -------------------------------------------------------
echo 1. PERFORMING HANDSHAKE (MySQL Simulation + MongoDB ACK)
echo -------------------------------------------------------

%PYTHON_EXE% mysql\persistence\handshake.py %PLAYER_ID%
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✘ HANDSHAKE FAILED.
    exit /b 1
)

echo.
echo -------------------------------------------------------
echo 2. STARTING REAL APP ^& MAZERUN GAME
echo -------------------------------------------------------

:: Start Persistence App in background
set PYTHONPATH=%CD%\mysql\persistence
start /B "MazeRun-Persistence" %PYTHON_EXE% mysql\persistence\app.py > persistence_session.log 2>&1
echo [Launcher] ✔ Persistence App started in background.

:: Start Game
set EXE_PATH=server\mazerun.exe
if exist "%EXE_PATH%" (
    echo [Launcher] Starting mazerun.exe ...
    start "" "%EXE_PATH%" %TEAM_ID% --flagMessage 1 --delay 2 --broker broker.hivemq.com --portbroker 1883
) else (
    echo [Launcher] ERROR: mazerun.exe not found!
    exit /b 1
)

echo.
echo Simulation is active! Enjoy the game.
echo Check logs with: type persistence_session.log
echo -------------------------------------------------------

endlocal