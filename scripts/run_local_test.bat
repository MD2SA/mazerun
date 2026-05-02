@echo off
echo === STARTING MAZERUN INFRASTRUCTURE (MONGO + MYSQL) ===

set /p reset_db="Do you want to RESET the databases? (This will DELETE ALL DATA and re-run SQL scripts) [y/N]: "

if /i "%reset_db%"=="y" (
    echo [Clean] Stopping services and removing volumes...
    cd mongo
    docker-compose down -v
    cd ..
    cd mysql
    docker-compose down -v
    cd ..
    echo [Clean] Reset complete.
)

:: 1. Start Mongo services (Inbound + Outbound)
echo [1/2] Starting MONGO services...
cd mongo
docker-compose up -d --build
cd ..

:: 2. Start MySQL DB (Database only, the App is started via session script)
echo [2/2] Starting MYSQL database...
cd mysql
:: We only start the db and phpmyadmin, mysql-app is handled by start_simulation.bat
docker-compose up -d mysql-db phpmyadmin
cd ..

echo -------------------------------------------------------
echo Infrastructure is running!
echo  - phpMyAdmin: http://localhost:8080
echo  - MongoDB:    localhost:27017
echo  - MySQL:      localhost:3306
echo.
echo -------------------------------------------------------
echo READY FOR SIMULATION!
echo To start a game session (handshake + persistence + game):
echo   scripts\start_simulation.bat ^<player_id^>
echo -------------------------------------------------------
