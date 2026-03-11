@echo off
setlocal EnableDelayedExpansion

set CONTAINER=mysql
set DB=mazerun
set USER=root
set PASSWORD=root
set CONTAINER_OUT=/backup/dump.sql

echo Creating full dump of database '%DB%' ...

docker exec %CONTAINER% ^
    bash -c "mysqldump -u%USER% -p%PASSWORD% ^
        --single-transaction ^
        --routines --triggers --events ^
        --set-gtid-purged=OFF ^
        --databases %DB% --add-drop-database --add-drop-table ^
        > %CONTAINER_OUT%" 2^>^&1 | findstr /V "insecure" 1^>^&2

if %ERRORLEVEL% EQU 0 (
    echo Done!
    echo File created inside container   ^> %CONTAINER_OUT%
    echo On your host computer it appears ^> .\dbs\mysql\dump.sql
    if exist ".\dbs\mysql\dump.sql" (
        dir ".\dbs\mysql\dump.sql"
    ) else (
        echo (check if the folder exists)
    )
) else (
    echo Error while running mysqldump. Please check:
    echo  • Is container '%CONTAINER%' running?
    echo  • Is the password correct?
    echo  • Does database '%DB%' exist?
)

echo.
pause
endlocal
