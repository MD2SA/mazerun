#!/bin/bash
# Script unificado: Faz o deploy de todos os serviços Mongo (Replica Set e App Python) via Docker

cd "$(dirname "$0")" || exit

echo "========================================="
echo " MAZERUN - INICIAR MONGODB (DOCKER)"
echo "========================================="
echo "A parar containers antigos (se existirem)..."
docker compose down

echo "A iniciar o Cluster MongoDB e a App Python..."
# O Docker Compose levanta o replica set, corre o mongo-setup e liga o mongo-app
docker compose up --build
