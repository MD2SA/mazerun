@echo off
REM Script para deploy do serviço MySQL Persistence usando Docker no Windows

echo Deploying MySQL Persistence Service via Docker...
cd /d "%~dp0"

echo Building and starting containers...
docker-compose up -d --build

echo Done!
