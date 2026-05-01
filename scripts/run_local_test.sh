#!/bin/bash

# Script to run all services locally for testing
echo "=== STARTING FULL LOCAL TEST (MONGO + MYSQL) ==="

# Ask for database reset
read -p "Do you want to RESET the databases? (This will DELETE ALL DATA and re-run SQL scripts) [y/N]: " reset_db

if [[ "$reset_db" =~ ^[Yy]$ ]]; then
    echo "[Clean] Stopping services and removing volumes..."
    (cd mongo && docker-compose down -v)
    (cd mysql && docker-compose down -v)
    echo "[Clean] Reset complete."
fi

# 1. Start Mongo services
echo "[1/2] Starting MONGO services..."
(cd mongo && docker-compose up -d --build)

# 2. Start MySQL services
echo "[2/2] Starting MYSQL services..."
(cd mysql && docker-compose up -d --build)

echo "-------------------------------------------------------"
echo "All services are running!"
echo "  - phpMyAdmin: http://localhost:8080"
echo "  - MongoDB:    localhost:27017"
echo "  - MySQL:      localhost:3306"
echo ""
echo "To see logs, use:"
echo "  - Mongo App:  docker logs -f mazerun-mongo-app"
echo "  - MySQL App:  docker logs -f mazerun-mysql-persistence"
echo "-------------------------------------------------------"
