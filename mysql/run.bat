@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set CONTAINER=mazerun-mysql-db
set DB_DIR=%~dp0db
set DB=%MYSQL_DATABASE%
if "%DB%"=="" set DB=mazerun
set USER=%MYSQL_USER%
if "%USER%"=="" set USER=root
set PASSWORD=%MYSQL_ROOT_PASSWORD%

if "%PASSWORD%"=="" (
    echo MYSQL_ROOT_PASSWORD is not set. Add it to mysql\.env or set it in the environment.
    exit /b 1
)

echo =========================================
echo  MAZERUN - INICIAR AMBIENTE (DOCKER)
echo =========================================

set /p APPLY_DUMP="Desejas aplicar as alteracoes a base de dados MySQL (recriar procedures, etc)? (y/n): "
echo.

echo A parar containers antigos (se existirem)...
docker compose down

echo A iniciar a base de dados em background para validar/aplicar procedures...
docker compose up -d mysql-db

echo A aguardar 10 segundos para o MySQL ficar pronto...
timeout /t 10 /nobreak >nul

if /I "%APPLY_DUMP%"=="y" (
    echo A aplicar dump completo e procedures da pasta mysql/db...
    echo  -^> A aplicar dump.sql...
    docker exec -i -e "MYSQL_PWD=%PASSWORD%" %CONTAINER% mysql -u%USER% %DB% < "%DB_DIR%\dump.sql"
    if errorlevel 1 exit /b 1
) else (
    echo A manter dados existentes; a reaplicar apenas procedures/roles...
)

echo  -^> A aplicar user_procedures.sql...
docker exec -i -e "MYSQL_PWD=%PASSWORD%" %CONTAINER% mysql -u%USER% %DB% < "%DB_DIR%\user_procedures.sql"
if errorlevel 1 exit /b 1

echo  -^> A aplicar simulation_procedures.sql...
docker exec -i -e "MYSQL_PWD=%PASSWORD%" %CONTAINER% mysql -u%USER% %DB% < "%DB_DIR%\simulation_procedures.sql"
if errorlevel 1 exit /b 1

echo  -^> A aplicar persistence_routines.sql...
docker exec -i -e "MYSQL_PWD=%PASSWORD%" %CONTAINER% mysql -u%USER% %DB% < "%DB_DIR%\persistence_routines.sql"
if errorlevel 1 exit /b 1

echo  -^> A aplicar roles.sql...
docker exec -i -e "MYSQL_PWD=%PASSWORD%" %CONTAINER% mysql -u%USER% %DB% < "%DB_DIR%\roles.sql"
if errorlevel 1 exit /b 1

echo Alteracoes aplicadas com sucesso!
echo -----------------------------------------

echo A iniciar todos os servicos (MySQL, PHPMyAdmin, PHP e App Python)...
docker compose up --build
