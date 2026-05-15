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

# 2. Active health-check: wait for MySQL to be ready (up to 90 seconds)
echo "[Wait] Probing MySQL readiness (up to 90s)..."
MAX_WAIT=90
WAITED=0
READY=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if docker exec mazerun-mysql-db mysqladmin ping -uroot -proot --silent >/dev/null 2>&1; then
        READY=1
        break
    fi
    sleep 3
    WAITED=$((WAITED + 3))
    echo "[Wait] MySQL not ready yet... (${WAITED}s elapsed)"
done

if [ $READY -eq 0 ]; then
    echo "[ERROR] MySQL did not become ready within ${MAX_WAIT} seconds."
    exit 1
fi

echo "[Wait] MySQL is ready! (${WAITED}s elapsed)"

# 3. Extra buffer for DB init scripts to finish running
sleep 5

# 4. Start Simulation
./scripts/start_simulation.sh "$PLAYER_ID"
