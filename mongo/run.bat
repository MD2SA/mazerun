@echo off
REM Script unificado: Faz o deploy de todos os serviços Mongo (Replica Set e App Python) via Docker

cd /d "%~dp0"

echo =========================================
echo  MAZERUN - INICIAR MONGODB (DOCKER)
echo =========================================
echo A parar containers antigos (se existirem)...
docker compose down

echo A iniciar o Cluster MongoDB e a App Python...
REM O Docker Compose levanta o replica set, corre o mongo-setup e liga o mongo-app
docker compose up --build
