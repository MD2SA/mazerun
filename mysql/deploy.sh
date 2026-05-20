#!/bin/bash
# Script para iniciar o ambiente MySQL (DB + App + PHPMyAdmin) em modo Detached (Servidor Real)

echo "A parar containers antigos do MySQL (se existirem)..."
docker compose down

echo "A reconstruir e iniciar o ambiente MySQL em modo 'detached'..."
docker compose up -d --build

echo "Ambiente MySQL iniciado com sucesso."
