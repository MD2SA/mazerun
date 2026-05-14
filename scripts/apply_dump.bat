@echo off
setlocal EnableDelayedExpansion

@echo off
setlocal EnableDelayedExpansion

set CONTAINER=mazerun-mysql-db
set DB=mazerun
set USER=root
set PASSWORD=root
set CONTAINER_FILE=/tmp/dump.sql

cd /d "%~dp0\.."
set HOST_DIR=.\mysql\db

echo Applying schema and procedures to database '%DB%' ...
echo.

:: Check if container is running
docker ps --filter "name=%CONTAINER%" --format "{{.Names}}" | findstr /I "%CONTAINER%" >nul
if errorlevel 1 (
    echo Error: Container %CONTAINER% is not running.
    echo Please start it with 'docker-compose up' first.
    pause
    exit /b 1
)

:: Apply dump.sql
echo [1/5] Applying base dump...
docker cp "%HOST_DIR%\dump.sql" %CONTAINER%:%CONTAINER_FILE%
docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"

:: Apply user_procedures.sql
echo [2/5] Applying user procedures...
docker cp "%HOST_DIR%\user_procedures.sql" %CONTAINER%:%CONTAINER_FILE%
docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"

:: Apply simulation_procedures.sql
echo [3/5] Applying simulation procedures...
docker cp "%HOST_DIR%\simulation_procedures.sql" %CONTAINER%:%CONTAINER_FILE%
docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"

:: Apply persistence_routines.sql
echo [4/5] Applying persistence routines...
docker cp "%HOST_DIR%\persistence_routines.sql" %CONTAINER%:%CONTAINER_FILE%
docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"

:: Apply roles.sql
echo [5/5] Applying roles...
docker cp "%HOST_DIR%\roles.sql" %CONTAINER%:%CONTAINER_FILE%
docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All database components applied successfully!
) else (
    echo.
    echo Error during application. Please check the output above.
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All database components applied successfully!
) else (
    echo.
    echo Error during application. Please check the output above.
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Schema applied successfully!
    echo Used file ^(container^): %CONTAINER_FILE%
    if "%host_exists%"=="yes" echo   ^(source on host: %HOST_FILE%^)
) else (
    echo.
    echo Error during import. Check:
    echo  • Container is running?
    echo  • Password is correct?
    echo  • Dump file is valid SQL?
    echo  • Try running manually: docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"
)

echo.
pause
endlocal
