@echo off
REM Script unificado: Faz o deploy de todos os serviços da Web-App via Docker

cd /d "%~dp0"

echo =========================================
echo  MAZERUN - INICIAR WEB-APP (DOCKER)
echo =========================================
echo A parar containers antigos (se existirem)...
docker compose down

echo A iniciar a Web-App...
REM Ao remover o "-d" e nomes especificos, o Docker Compose levanta a infraestrutura 
REM toda e fica agarrado ao terminal a mostrar os logs da aplicacao.
docker compose up --build
