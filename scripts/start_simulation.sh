#!/bin/bash

# Script to start a new MazeRun simulation session
# Usage: ./start_simulation.sh <player_id>

TEAM_ID=25
PLAYER_ID=$1

if [ -z "$PLAYER_ID" ]; then
    echo "Usage: $0 <player_id>"
    exit 1
fi

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# --- VENV MANAGEMENT ---
# Check if a virtual environment exists, if not create one
PYTHON_EXE="python3"
if [ ! -d "./venv" ]; then
    echo "[Launcher] Creating virtual environment (venv)..."
    python3 -m venv venv
fi

if [ -f "./venv/bin/activate" ]; then
    echo "[Launcher] Activating venv and checking dependencies..."
    source ./venv/bin/activate
    pip install -r mysql/persistence/requirements.txt > /dev/null 2>&1
    PYTHON_EXE="python"
fi
# ----------------------

echo "-------------------------------------------------------"
echo "1. PERFORMING HANDSHAKE (MySQL Simulation + MongoDB ACK)"
echo "-------------------------------------------------------"

# Run the handshake script
# This script creates the simulation in MySQL, notifies MongoDB, and waits for ACK.
$PYTHON_EXE mysql/persistence/handshake.py "$PLAYER_ID"

if [ $? -eq 0 ]; then
    echo ""
    echo "-------------------------------------------------------"
    echo "2. STARTING REAL APP & MAZERUN GAME"
    echo "-------------------------------------------------------"
    
    # 1. Start the Persistence Service (The Real App) in the background
    # Note: Using PYTHONPATH to ensure common modules are found
    export PYTHONPATH=$PYTHONPATH:$(pwd)/mysql/persistence
    $PYTHON_EXE mysql/persistence/app.py > persistence_session.log 2>&1 &
    APP_PID=$!
    echo "[Launcher] ✔ Persistence App started (PID: $APP_PID)."
    echo "[Launcher] NOTE: Logs are now in 'persistence_session.log' (use: tail -f persistence_session.log)"

    # 2. Start the MazeRun Game
    echo "[Launcher] Starting mazerun.exe with arguments..."
    
    EXE_PATH="game/server/mazerun.exe"
    wine "$EXE_PATH" $TEAM_ID --flagMessage 1 --delay 2 --broker broker.hivemq.com --portbroker 1883 > /dev/null 2>&1 &
    
    GAME_PID=$!
    echo "[Launcher] Game started (PID: $GAME_PID)"

    echo "-------------------------------------------------------"
    echo "Simulation is active! Enjoy the game."
    echo "The persistence service will stop automatically when you close this script."
    echo "-------------------------------------------------------"

    # Function to cleanup on exit
    cleanup() {
        echo ""
        echo "[Launcher] Stopping simulation session..."
        kill $APP_PID 2>/dev/null
        echo "[Launcher] Persistence App stopped."
        exit
    }

    trap cleanup SIGINT SIGTERM

    # Wait for the game process to finish
    wait $GAME_PID
    echo "[Launcher] Game process finished."
    cleanup
else
    echo ""
    echo "-------------------------------------------------------"
    echo "✘ HANDSHAKE FAILED. Simulation cannot start safely."
    echo "Ensure that MongoDB and MySQL services are running."
    echo "-------------------------------------------------------"
    exit 1
fi
