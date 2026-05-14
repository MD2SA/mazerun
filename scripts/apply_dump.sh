#!/usr/bin/env bash
set -euo pipefail

CONTAINER="mazerun-mysql-db"
DB="mazerun"
USER="root"
PASSWORD="root"
CONTAINER_FILE="/tmp/dump.sql"

# Get project root
cd "$(dirname "$0")/.."
HOST_DIR="./mysql/db"

echo "Applying schema and procedures to database '$DB' ..."

# Check if container is running
if ! docker ps --filter "name=$CONTAINER" --format "{{.Names}}" | grep -q "$CONTAINER"; then
    echo "Error: Container $CONTAINER is not running."
    echo "Please start it with 'docker-compose up' first."
    exit 1
fi

apply_sql() {
    local file=$1
    echo "Applying $file..."
    docker cp "$HOST_DIR/$file" "$CONTAINER:$CONTAINER_FILE"
    docker exec "$CONTAINER" bash -c "mysql -u$USER -p$PASSWORD $DB < $CONTAINER_FILE"
}

apply_sql "dump.sql"
apply_sql "user_procedures.sql"
apply_sql "simulation_procedures.sql"
apply_sql "persistence_routines.sql"
apply_sql "roles.sql"

echo "All database components applied successfully!"
