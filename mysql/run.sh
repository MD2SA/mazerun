#!/bin/bash
# Script unificado: Faz o deploy de todos os serviços (Base de Dados, Web e App Python) via Docker

cd "$(dirname "$0")" || exit

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
until docker exec mazerun-mysql-db mysqladmin ping -proot --silent &> /dev/null; do
    sleep 2
done

HOST_DIR="./db"
CONTAINER="mazerun-mysql-db"
CONTAINER_FILE="/tmp/mazerun.sql"
DB="mazerun"

apply_sql() {
    local file=$1
    echo " -> A aplicar $file..."
    docker cp "$HOST_DIR/$file" "$CONTAINER:$CONTAINER_FILE"
    docker exec "$CONTAINER" bash -c "mysql -uroot -proot $DB < $CONTAINER_FILE"
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

echo "A iniciar todos os serviços (MySQL, PHPMyAdmin, PHP e App Python)..."
# Ao remover o "-d" e nomes específicos, o Docker Compose levanta a infraestrutura 
# toda e fica agarrado ao terminal a mostrar os logs de todos os serviços (incluindo o Python).
docker compose up --build
