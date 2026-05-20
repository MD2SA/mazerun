@echo off
REM Script para iniciar a Web App (Node/React) localmente no Windows

echo Starting Web App...
cd /d "%~dp0"

REM Usar pnpm se estiver disponível, caso contrário usar npm
where pnpm >nul 2>nul
if %errorlevel%==0 (
    echo Using pnpm...
    call pnpm install
    echo Running Vite dev server...
    call pnpm run dev
) else (
    echo Using npm...
    call npm install
    echo Running Vite dev server...
    call npm run dev
)
