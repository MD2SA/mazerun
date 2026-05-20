#!/bin/bash
# Script unificado: Faz o deploy de todos os serviços da Web-App via Docker

cd "$(dirname "$0")" || exit

echo "========================================="
echo " MAZERUN - INICIAR WEB-APP (DOCKER)"
echo "========================================="
echo "A parar containers antigos (se existirem)..."
docker compose down

echo "A iniciar a Web-App..."
# Ao remover o "-d" e nomes específicos, o Docker Compose levanta a infraestrutura 
# toda e fica agarrado ao terminal a mostrar os logs da aplicação.
docker compose up --build
