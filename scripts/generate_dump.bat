@echo off
setlocal EnableExtensions EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
set CONTAINER=mazerun-mysql-db
set DB=mazerun
set USER=root
set PASSWORD=%MYSQL_ROOT_PASSWORD%
if "%PASSWORD%"=="" (
    echo MYSQL_ROOT_PASSWORD is not set. Add it to mysql\.env or export it.
    exit /b 1
)
set HOST_OUT=%REPO_ROOT%\mysql\db\dump.sql

if not exist "%REPO_ROOT%\mysql\db" mkdir "%REPO_ROOT%\mysql\db"

echo Creating full dump of database '%DB%' ...
docker exec -e MYSQL_PWD=%PASSWORD% %CONTAINER% mysqldump -u%USER% --single-transaction --routines --triggers --events --set-gtid-purged=OFF --databases %DB% --add-drop-database --add-drop-table > "%HOST_OUT%"

if %ERRORLEVEL% EQU 0 (
    echo Done: %HOST_OUT%
    dir "%HOST_OUT%"
) else (
    echo Error while running mysqldump. Please check:
    echo  - Is container '%CONTAINER%' running?
    echo  - Is MYSQL_ROOT_PASSWORD correct?
    echo  - Does database '%DB%' exist?
)

echo.
pause
endlocal
