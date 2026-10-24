#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load local credentials when present.
if [ -f "$REPO_ROOT/mysql/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$REPO_ROOT/mysql/.env"
  set +a
fi

CONTAINER="${MYSQL_CONTAINER:-mazerun-mysql-db}"
DB="${MYSQL_DATABASE:-mazerun}"
USER="${MYSQL_USER:-root}"
PASSWORD="${MYSQL_ROOT_PASSWORD:-}"
HOST_OUT="$REPO_ROOT/mysql/db/dump.sql"

if [ -z "$PASSWORD" ]; then
  echo "MYSQL_ROOT_PASSWORD is not set. Add it to mysql/.env or export it." >&2
  exit 1
fi

if ! docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
  echo "Container '$CONTAINER' is not running. Start the MySQL stack first." >&2
  exit 1
fi

mkdir -p "$(dirname "$HOST_OUT")"
echo "Creating full dump of database '$DB' ..."

docker exec -e MYSQL_PWD="$PASSWORD" "$CONTAINER" \
  mysqldump -u"$USER" \
    --single-transaction \
    --routines --triggers --events \
    --set-gtid-purged=OFF \
    --databases "$DB" --add-drop-database --add-drop-table \
  > "$HOST_OUT"

echo "Done: $HOST_OUT"
ls -lh "$HOST_OUT"
