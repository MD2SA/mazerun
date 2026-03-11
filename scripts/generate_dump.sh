#!/usr/bin/env bash

CONTAINER="mysql"
DB="mazerun"
USER="root"
PASSWORD="root"
CONTAINER_OUT="/backup/dump.sql"

echo "Creating full dump of database '$DB' ..."

# Run mysqldump inside the container and redirect output there
docker exec "$CONTAINER" \
    bash -c "mysqldump -u$USER -p$PASSWORD \
        --single-transaction \
        --routines --triggers --events \
        --set-gtid-purged=OFF \
        --databases $DB --add-drop-database --add-drop-table \
        > $CONTAINER_OUT" 2> >(grep -v "insecure" >&2)

if [ $? -eq 0 ]; then
    echo "Done!"
    echo "File created inside container   → $CONTAINER_OUT"
    echo "On your host computer it appears → ./dbs/mysql/dump.sql"
    ls -lh ./dbs/mysql/dump.sql 2>/dev/null || echo "(check if the folder exists)"
else
    echo "Error while running mysqldump. Please check:"
    echo " • Is container '$CONTAINER' running?"
    echo " • Is the password correct?"
    echo " • Does database '$DB' exist?"
fi
