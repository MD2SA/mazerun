@echo off
REM Script para deploy do serviço Mongo usando Docker no Windows

echo Deploying Mongo Microservice via Docker...
cd /d "%~dp0"

echo Building and starting containers...
docker-compose up -d --build

echo Done!
