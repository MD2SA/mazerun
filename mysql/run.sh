#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load local credentials when present.
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$SCRIPT_DIR/.env"
  set +a
fi

CONTAINER="mazerun-mysql-db"
DB_DIR="$SCRIPT_DIR/db"
DB="${MYSQL_DATABASE:-mazerun}"
USER="${MYSQL_USER:-root}"
PASSWORD="${MYSQL_ROOT_PASSWORD:-}"

if [ -z "$PASSWORD" ]; then
  echo "MYSQL_ROOT_PASSWORD is not set. Add it to mysql/.env or export it." >&2
  exit 1
fi

echo "========================================="
echo " MAZERUN - INICIAR AMBIENTE (DOCKER)"
echo "========================================="

read -p "Desejas aplicar as alteracoes a base de dados MySQL (recriar procedures, etc)?
Esta acção vai apagar todos os dados existentes. Continuar? (y/N) " -n 1 -r
echo
APPLY_DUMP=$REPLY

echo "A parar containers antigos (se existirem)..."
docker compose down

echo "A iniciar a base de dados em background para validar/aplicar procedures..."
docker compose up -d mysql-db

echo "A aguardar que o MySQL fique pronto (pode demorar alguns segundos)..."
until docker exec -e MYSQL_PWD="$PASSWORD" "$CONTAINER" mysqladmin ping --silent &> /dev/null; do
  sleep 2
done

apply_sql() {
  local file="$1"
  echo " -> A aplicar $file..."
  docker exec -i -e MYSQL_PWD="$PASSWORD" "$CONTAINER" \
    mysql -u"$USER" "$DB" < "$DB_DIR/$file"
}

if [[ $APPLY_DUMP =~ ^[Yy]$ ]]; then
  echo "A aplicar dump completo e procedures da pasta mysql/db..."
  apply_sql "dump.sql"
else
  echo "A manter dados existentes; a reaplicar apenas procedures/roles..."
fi

apply_sql "user_procedures.sql"
apply_sql "simulation_procedures.sql"
apply_sql "persistence_routines.sql"
apply_sql "roles.sql"

echo "Alteracoes aplicadas com sucesso!"
echo "-----------------------------------------"

echo "A iniciar todos os servicos (MySQL, PHPMyAdmin, PHP e App Python)..."
docker compose up --build
