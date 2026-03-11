@echo off
setlocal EnableDelayedExpansion

set CONTAINER=mysql
set DB=mazerun
set USER=root
set PASSWORD=root
set HOST_FILE=.\dbs\mysql\dump.sql
set CONTAINER_FILE=/backup/dump.sql

echo Applying schema to database '%DB%' ...
echo.

:: Verificar existência nos dois lados
set host_exists=no
set container_exists=no

if exist "%HOST_FILE%" set host_exists=yes

docker exec %CONTAINER% test -f %CONTAINER_FILE% >nul 2>&1
if %ERRORLEVEL% EQU 0 set container_exists=yes

if "%host_exists%"=="no" if "%container_exists%"=="no" (
    echo Error: Dump file not found in EITHER location!
    echo   Host:      %HOST_FILE%
    echo   Container: %CONTAINER_FILE%
    echo.
    pause
    exit /b 1
)

:: Só no container → usa direto
if "%host_exists%"=="no" if "%container_exists%"=="yes" (
    echo File found ONLY inside container → using it directly
    set should_copy=no
    goto :import_step
)

:: Existe no host (pode ou não existir no container)
set should_copy=yes

if "%container_exists%"=="yes" (
    echo File already exists inside container: %CONTAINER_FILE%

    :: Hash MD5 host
    for /f "skip=1 tokens=* delims=" %%# in ('certutil -hashfile "%HOST_FILE%" MD5 ^| findstr /v ":"') do set "host_md5=%%#"
    set "host_md5=!host_md5: =!"

    :: Hash MD5 container
    for /f "delims=" %%# in ('docker exec %CONTAINER% certutil -hashfile %CONTAINER_FILE% MD5 ^| findstr /v ":"') do set "cont_md5=%%#"
    set "cont_md5=!cont_md5: =!"

    if "!host_md5!"=="!cont_md5!" if not "!host_md5!"=="" (
        echo Files are identical (same MD5) → skipping copy
        set should_copy=no
    ) else (
        echo Files are different (or hash failed) → will copy/overwrite
    )
) else (
    echo File exists only on host → will copy
)

if "%should_copy%"=="yes" (
    echo.
    echo Copying dump file into container...
    docker cp "%HOST_FILE%" %CONTAINER%:%CONTAINER_FILE%
    if errorlevel 1 (
        echo Error: Failed to copy file to container.
        pause
        exit /b 1
    )
) else (
    echo Skipping copy ^(already present and identical or only in container^)
)

:import_step

:: Confirma que existe dentro do container
docker exec %CONTAINER% test -f %CONTAINER_FILE% >nul 2>&1
if errorlevel 1 (
    echo Error: Something went wrong - file is still not present in container
    pause
    exit /b 1
)

echo.
echo Dropping and recreating database ^(this will delete all current data!^)...
docker exec %CONTAINER% mysql -u%USER% -p%PASSWORD% -e "DROP DATABASE IF EXISTS %DB%; CREATE DATABASE %DB%;"

echo.
echo Importing from container path: %CONTAINER_FILE% ...
docker exec %CONTAINER% bash -c "mysql -u%USER% -p%PASSWORD% %DB% < %CONTAINER_FILE%"

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
