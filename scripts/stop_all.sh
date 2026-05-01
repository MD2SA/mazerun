#!/bin/bash
echo "=== STOPPING ALL MAZERUN SERVICES ==="

echo "[1/2] Stopping MONGO services..."
(cd mongo && docker-compose down)

echo "[2/2] Stopping MYSQL services..."
(cd mysql && docker-compose down)

echo "Done. All containers stopped."
