#!/bin/bash
# Script para iniciar o ambiente Web-App em modo Detached (Servidor Real)

echo "A parar containers antigos da Web-App (se existirem)..."
docker compose down

echo "A reconstruir e iniciar a Web-App em modo 'detached'..."
docker compose up -d --build

echo "Web-App iniciada com sucesso. Disponível na porta 80."
