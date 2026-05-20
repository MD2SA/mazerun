@echo off
REM Script para iniciar o serviço Python do Mongo localmente no Windows

echo Starting Mongo Microservice...
cd /d "%~dp0"

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
echo Running main.py...
python main.py
