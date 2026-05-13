@echo off
setlocal

:: Script to start a new MazeRun simulation session on Windows
:: Usage: scripts\start_simulation.bat <player_id>

set TEAM_ID=25
set PLAYER_ID=%1

if "%PLAYER_ID%"=="" (
    echo Usage: %0 ^<player_id^>
    exit /b 1
)

:: Ensure we are in the project root
cd %~dp0\..

:: --- AUTO-CREATE VENV IF NEEDED ---
if not exist "venv\Scripts\activate.bat" (
    if not exist "mysql\persistence\venv\Scripts\activate.bat" (
        if not exist "mongo\venv\Scripts\activate.bat" (
            echo [Setup] No virtual environment found. Creating venv in project root...
            python -m venv venv
            if %ERRORLEVEL% NEQ 0 (
                echo ✘ ERROR: Failed to create virtual environment
                exit /b 1
            )
            echo [Setup] Virtual environment created successfully!
        )
    )
)
:: ----------------------

:: --- VENV DETECTION ---
set PYTHON_EXE=python
if exist "venv\Scripts\activate.bat" (
    echo [Launcher] Using venv from project root
    call venv\Scripts\activate.bat
    set PYTHON_EXE=%CD%\venv\Scripts\python.exe
) else if exist "mysql\persistence\venv\Scripts\activate.bat" (
    echo [Launcher] Using venv from mysql\persistence
    call mysql\persistence\venv\Scripts\activate.bat
    set PYTHON_EXE=%CD%\mysql\persistence\venv\Scripts\python.exe
) else if exist "mongo\venv\Scripts\activate.bat" (
    echo [Launcher] Using venv from mongo directory
    call mongo\venv\Scripts\activate.bat
    set PYTHON_EXE=%CD%\mongo\venv\Scripts\python.exe
)
:: ----------------------

:: Install Python dependencies automatically
echo [Setup] Installing Python dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo ✘ WARNING: Failed to install some dependencies. Continuing anyway...
)

echo -------------------------------------------------------
echo 1. PERFORMING HANDSHAKE (MySQL Simulation + MongoDB ACK)
echo -------------------------------------------------------

:: Run the handshake script
"%PYTHON_EXE%" mysql\persistence\handshake.py %PLAYER_ID%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo -------------------------------------------------------
    echo 2. STARTING REAL APP ^& MAZERUN GAME
    echo -------------------------------------------------------
    

    :: 1. Start the Persistence Service (The Real App) in the background
    :: On Windows, we use 'start' to run in a new minimized window or hidden
    set PYTHONPATH=%PYTHONPATH%;%CD%\mysql\persistence
    start /B "MazeRunPersistence" "%PYTHON_EXE%" mysql\persistence\app.py ^> persistence_session.log 2^>^&1
    echo [Launcher] Persistence App started in background. Logs: persistence_session.log

    :: 2. Start the MazeRun Game
    echo [Launcher] Starting mazerun.exe with arguments...
    
    set EXE_PATH=game\server\mazerun.exe
    if exist %EXE_PATH% (
        start "" "%EXE_PATH%" %TEAM_ID% --flagMessage 1 --delay 2 --broker broker.hivemq.com --portbroker 1883
        echo [Launcher] Game started.
    ) else (
        echo [Launcher] ERROR: mazerun.exe not found at %EXE_PATH%
        exit /b 1
    )

    echo -------------------------------------------------------
    echo Simulation is active! Enjoy the game.
    echo.
    echo IMPORTANT: Close the Persistence App window or task when finished.
    echo -------------------------------------------------------
    
) else (
    echo.
    echo -------------------------------------------------------
    echo ✘ HANDSHAKE FAILED. Simulation cannot start safely.
    echo Ensure that MongoDB and MySQL services are running.
    echo -------------------------------------------------------
    exit /b 1
)

exit /b 0
