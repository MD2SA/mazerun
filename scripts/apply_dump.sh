#!/usr/bin/env bash
set -euo pipefail

CONTAINER="mysql"
DB="mazerun"
USER="root"
PASSWORD="root"
HOST_FILE="./dbs/mysql/dump.sql"
CONTAINER_FILE="/backup/dump.sql"

echo "Applying schema to database '$DB' ..."

host_exists=false
container_exists=false

if [[ -f "$HOST_FILE" ]]; then
    host_exists=true
fi

if docker exec "$CONTAINER" test -f "$CONTAINER_FILE" 2>/dev/null; then
    container_exists=true
fi

if ! $host_exists && ! $container_exists; then
    echo "Error: Dump file not found in EITHER location!"
    echo "  • Host:     $HOST_FILE"
    echo "  • Container: $CONTAINER_FILE"
    exit 1
fi

if ! $host_exists && $container_exists; then
    echo " → File found ONLY inside container → using it directly"
    should_copy=false
else
    should_copy=true

    if $container_exists; then
        echo " → File already exists inside container: $CONTAINER_FILE"

        host_md5=$(md5sum "$HOST_FILE" 2>/dev/null | awk '{print $1}' || \
                   md5 -r "$HOST_FILE" 2>/dev/null | awk '{print $1}' || echo "unknown")
        cont_md5=$(docker exec "$CONTAINER" md5sum "$CONTAINER_FILE" 2>/dev/null | awk '{print $1}' || \
                   docker exec "$CONTAINER" md5 -r "$CONTAINER_FILE" 2>/dev/null | awk '{print $1}' || echo "unknown")

        if [[ "$host_md5" == "$cont_md5" && "$host_md5" != "unknown" ]]; then
            echo " → Files are identical → skipping copy"
            should_copy=false
        else
            echo " → Files differ (or checksum unavailable) → will copy/overwrite"
        fi
    else
        echo " → File exists only on host → will copy"
    fi

    if $should_copy; then
        echo "Copying dump file into container..."
        docker cp "$HOST_FILE" "$CONTAINER:$CONTAINER_FILE"
    else
        echo "Skipping copy"
    fi
fi

docker exec "$CONTAINER" test -f "$CONTAINER_FILE" || {
    echo "Error: File is not present inside the container at $CONTAINER_FILE"
    exit 1
}

echo "Dropping and recreating database..."
docker exec "$CONTAINER" mysql -u"$USER" -p"$PASSWORD" -e "DROP DATABASE IF EXISTS $DB; CREATE DATABASE $DB;"

echo "Importing from: $CONTAINER_FILE"
docker exec "$CONTAINER" bash -c "mysql -u'$USER' -p'$PASSWORD' '$DB' < '$CONTAINER_FILE'"

if [ $? -eq 0 ]; then
    echo "Schema applied successfully!"
    echo "Used file (container): $CONTAINER_FILE"
    if $host_exists; then
        echo "  (source on host: $HOST_FILE)"
    fi
else
    echo "Import failed — check mysql logs inside container:"
    echo "  docker logs $CONTAINER | tail -n 30"
fi
