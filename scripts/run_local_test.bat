@echo off
echo === STARTING MAZERUN INFRASTRUCTURE (MONGO + MYSQL) ===

set /p reset_db="Do you want to RESET the databases? (This will DELETE ALL DATA) [Y/N]: "

if /i "%reset_db%"=="y" (
    echo [Clean] Stopping services and removing volumes...
    pushd mongo && docker-compose down -v && popd
    pushd mysql && docker-compose down -v && popd
    echo [Clean] Reset complete.
)

:: 1. Start Mongo services
echo [1/2] Starting MONGO services...
pushd mongo && docker-compose up -d --build && popd

:: 2. Start MySQL (only DB + phpMyAdmin)
echo [2/2] Starting MYSQL database...
pushd mysql && docker-compose up -d mysql-db phpmyadmin && popd

echo -------------------------------------------------------
echo Infrastructure is running!
echo   - phpMyAdmin: http://localhost:8080
echo   - MongoDB:    localhost:27017
echo   - MySQL:      localhost:3306
echo -------------------------------------------------------
echo READY FOR SIMULATION!
echo scripts\start_simulation.bat ^<player_id^>
echo -------------------------------------------------------
