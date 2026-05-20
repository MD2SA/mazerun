@echo off
REM Script para iniciar o serviço Python do MySQL (Persistence) localmente no Windows

echo Starting MySQL Persistence Service...
cd /d "%~dp0persistence"

REM Criar ambiente virtual se não existir
IF NOT EXIST "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Ativar ambiente virtual e instalar dependências
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

REM Executar o serviço
echo Running app.py...
python app.py
