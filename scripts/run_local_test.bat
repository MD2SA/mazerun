@echo off
echo === STARTING FULL LOCAL TEST (MONGO + MYSQL) ===

:: 1. Start Mongo services
echo [1/2] Starting MONGO services...
cd mongo
docker-compose up -d --build
cd ..

:: 2. Start MySQL services
echo [2/2] Starting MYSQL services...
cd mysql
docker-compose up -d --build
cd ..

echo -------------------------------------------------------
echo All services are running!
echo  - phpMyAdmin: http://localhost:8080
echo  - MongoDB:    localhost:27017
echo  - MySQL:      localhost:3306
echo.
echo To see logs, use:
echo  - Mongo App:  docker logs -f mazerun-mongo-app
echo  - MySQL App:  docker logs -f mazerun-mysql-persistence
echo -------------------------------------------------------
pause
