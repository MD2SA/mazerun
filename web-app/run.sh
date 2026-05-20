#!/bin/bash
# Script para iniciar a Web App (Node/React) localmente

echo "Starting Web App..."
cd "$(dirname "$0")" || exit

# Usar pnpm se estiver disponível, caso contrário usar npm
if command -v pnpm &> /dev/null; then
    echo "Using pnpm..."
    pnpm install
    echo "Running Vite dev server..."
    pnpm run dev
else
    echo "Using npm..."
    npm install
    echo "Running Vite dev server..."
    npm run dev
fi
