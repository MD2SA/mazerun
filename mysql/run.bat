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

if /I "%APPLY_DUMP%"=="y" (
    echo A iniciar apenas a base de dados em background para aplicar scripts...
    docker compose up -d mysql-db
    
    echo A aguardar 10 segundos para o MySQL ficar pronto...
    timeout /t 10 /nobreak >nul
    
    echo A aplicar ficheiros SQL da pasta mysql/db...
    
    echo  -^> A aplicar dump.sql...
    docker cp .\db\dump.sql mazerun-mysql-db:/tmp/dump.sql
    docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/dump.sql"
    
    echo  -^> A aplicar user_procedures.sql...
    docker cp .\db\user_procedures.sql mazerun-mysql-db:/tmp/dump.sql
    docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/dump.sql"
    
    echo  -^> A aplicar simulation_procedures.sql...
    docker cp .\db\simulation_procedures.sql mazerun-mysql-db:/tmp/dump.sql
    docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/dump.sql"
    
    echo  -^> A aplicar persistence_routines.sql...
    docker cp .\db\persistence_routines.sql mazerun-mysql-db:/tmp/dump.sql
    docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/dump.sql"
    
    echo  -^> A aplicar roles.sql...
    docker cp .\db\roles.sql mazerun-mysql-db:/tmp/dump.sql
    docker exec mazerun-mysql-db bash -c "mysql -uroot -proot mazerun < /tmp/dump.sql"
    
    echo Alteracoes aplicadas com sucesso!
    echo -----------------------------------------
)

echo A iniciar todos os serviços (MySQL, PHPMyAdmin, PHP e App Python)...
docker compose up --build
