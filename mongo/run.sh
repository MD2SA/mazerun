#!/bin/bash
# Script para iniciar o serviço Python do Mongo localmente

echo "Starting Mongo Microservice..."
cd "$(dirname "$0")" || exit

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Ativar ambiente virtual e instalar dependências
source venv/bin/activate
pip install -r requirements.txt

# Executar o serviço
echo "Running main.py..."
python main.py
