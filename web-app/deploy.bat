@echo off
REM Script para deploy da Web App usando Docker no Windows

echo Deploying Web App via Docker...
cd /d "%~dp0"

echo Building and starting containers...
docker-compose up -d --build

echo Done!
