#!/bin/bash
# Script para iniciar o ambiente Mongo (DB + App) em modo Detached (Servidor Real)

echo "A parar containers antigos do Mongo (se existirem)..."
docker compose down

echo "A reconstruir e iniciar o ambiente Mongo em modo 'detached'..."
docker compose up -d --build

echo "Ambiente Mongo iniciado com sucesso."
