@echo off
REM Script unificado: Faz o deploy de todos os serviços via Docker

cd /d "%~dp0"

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
    docker cp .\db\dump.sql mazerun-mysql-db:/tmp/mazerun.sql
    docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/mazerun.sql"
) else (
    echo A manter dados existentes; a reaplicar apenas procedures/roles...
)

echo  -^> A aplicar user_procedures.sql...
docker cp .\db\user_procedures.sql mazerun-mysql-db:/tmp/mazerun.sql
docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/mazerun.sql"

echo  -^> A aplicar simulation_procedures.sql...
docker cp .\db\simulation_procedures.sql mazerun-mysql-db:/tmp/mazerun.sql
docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/mazerun.sql"

echo  -^> A aplicar persistence_routines.sql...
docker cp .\db\persistence_routines.sql mazerun-mysql-db:/tmp/mazerun.sql
docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/mazerun.sql"

echo  -^> A aplicar roles.sql...
docker cp .\db\roles.sql mazerun-mysql-db:/tmp/mazerun.sql
docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/mazerun.sql"

echo Alteracoes aplicadas com sucesso!
echo -----------------------------------------

echo A iniciar todos os serviços (MySQL, PHPMyAdmin, PHP e App Python)...
docker compose up --build
