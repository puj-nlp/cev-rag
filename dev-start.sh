#!/bin/bash

# Script para iniciar el entorno de desarrollo
echo "Iniciando entorno de desarrollo RAG..."
echo "NOTA: El frontend estará disponible en http://localhost:3000"
echo "      La API estará disponible en http://localhost:8000"
echo ""

# Detener los contenedores existentes si están corriendo
echo "Deteniendo servicios previos si existen..."
docker compose -f docker-compose.dev.yml down

# Iniciar los servicios
echo "Iniciando los servicios..."
docker compose -f docker-compose.dev.yml up --build
