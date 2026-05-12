#!/bin/bash

# Unified script to start infrastructure and immediately trigger a simulation
# Usage: ./scripts/run_full_test.sh <player_id>

PLAYER_ID=$1

if [ -z "$PLAYER_ID" ]; then
    echo "Usage: $0 <player_id>"
    exit 1
fi

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# 1. Start Infrastructure
./scripts/run_local_test.sh

# 2. Wait for databases to be ready
echo "Waiting 5 seconds for infrastructure to settle..."
sleep 5

# 3. Start Simulation
./scripts/start_simulation.sh "$PLAYER_ID"
