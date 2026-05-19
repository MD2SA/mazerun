#!/bin/bash

# Script to run infrastructure locally for testing
echo "=== STARTING MAZERUN INFRASTRUCTURE (MONGO + MYSQL) ==="

# Ask for database reset
read -p "Do you want to RESET the databases? (This will DELETE ALL DATA and re-run SQL scripts) [Y/N]: " reset_db

if [[ "$reset_db" =~ ^[Yy]$ ]]; then
    echo "[Clean] Stopping services and removing volumes..."
    (cd mongo && docker-compose down -v)
    (cd mysql && docker-compose down -v)
    echo "[Clean] Reset complete."
fi

# 1. Start Mongo services (Inbound + Outbound)
echo "[1/2] Starting MONGO services..."
(cd mongo && docker-compose up -d --build)

# 2. Start MySQL DB (Database only, the App is started via session script)
echo "[2/2] Starting MYSQL database..."
# We only start the db and phpmyadmin, mysql-app is handled by start_simulation.sh
(cd mysql && docker-compose up -d --build)

echo "-------------------------------------------------------"
echo "Infrastructure is running!"
echo "  - phpMyAdmin: http://localhost:8080"
echo "  - MongoDB:    localhost:27017"
echo "  - MySQL:      localhost:3306"
echo ""
echo "-------------------------------------------------------"
echo "READY FOR SIMULATION!"
echo "To start a game session (handshake + persistence + game):"
echo "  ./scripts/start_simulation.sh <player_id>"
echo "-------------------------------------------------------"
