#!/bin/bash
# Script para iniciar y probar la API REST de Centinela Digital

set -e

echo "======================================================================"
echo "🚀 CENTINELA DIGITAL - API REST v2.0"
echo "======================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 no está instalado${NC}"
    exit 1
fi

# Verificar dependencias
echo -e "${BLUE}📋 Verificando dependencias...${NC}"
python3 -c "import flask, flask_cors, requests" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Instalando dependencias...${NC}"
    pip install flask flask-cors requests -q
}

echo -e "${GREEN}✓ Dependencias OK${NC}"
echo ""

# Menú de opciones
echo -e "${BLUE}Selecciona una opción:${NC}"
echo "  1) Iniciar servidor API (background)"
echo "  2) Iniciar servidor API (foreground)"
echo "  3) Ejecutar ejemplos (requiere servidor corriendo)"
echo "  4) Ejecutar tests"
echo "  5) Ver documentación"
echo ""

read -p "Opción (1-5): " option

case $option in
    1)
        echo -e "${BLUE}🌐 Iniciando servidor en background...${NC}"
        nohup python3 api.py > api.log 2>&1 &
        PID=$!
        echo -e "${GREEN}✓ Servidor iniciado (PID: $PID)${NC}"
        echo "Log: api.log"
        echo ""
        sleep 2
        
        # Verificar que esté corriendo
        if curl -s http://localhost:5000/health > /dev/null; then
            echo -e "${GREEN}✓ API accesible en http://localhost:5000${NC}"
            echo ""
            echo "Endpoints disponibles:"
            echo "  POST   /api/analyze                  - Analizar documento"
            echo "  GET    /api/case/<id>                - Obtener caso"
            echo "  GET    /api/cases                    - Listar casos"
            echo "  GET    /api/metrics/institutional    - Métricas"
            echo "  GET    /api/metrics/temporal         - Temporal"
            echo "  GET    /api/info                     - Información"
            echo ""
            echo "Detener servidor: kill $PID"
        else
            echo -e "${RED}❌ Error: No se pudo conectar a la API${NC}"
            exit 1
        fi
        ;;
    
    2)
        echo -e "${BLUE}🌐 Iniciando servidor (foreground)...${NC}"
        echo "API corriendo en http://localhost:5000"
        echo "Press Ctrl+C para detener"
        echo ""
        python3 api.py
        ;;
    
    3)
        echo -e "${BLUE}🧪 Ejecutando ejemplos...${NC}"
        echo ""
        
        # Verificar que el servidor está corriendo
        if ! curl -s http://localhost:5000/health > /dev/null; then
            echo -e "${RED}❌ Error: El servidor API no está corriendo${NC}"
            echo "Inicia el servidor primero con la opción 1 o 2"
            exit 1
        fi
        
        echo -e "${GREEN}✓ Servidor conectado${NC}"
        echo ""
        
        read -p "Qué ejemplo quieres ejecutar? (1-5, Enter para todos): " example
        
        if [ -z "$example" ]; then
            for i in 1 2 3 4 5; do
                echo ""
                echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
                python3 api_client.py $i
                sleep 1
            done
        else
            python3 api_client.py $example
        fi
        ;;
    
    4)
        echo -e "${BLUE}🧪 Ejecutando tests...${NC}"
        echo ""
        python3 test_runner.py
        ;;
    
    5)
        if command -v less &> /dev/null; then
            less API_DOCUMENTATION.md
        else
            cat API_DOCUMENTATION.md
        fi
        ;;
    
    *)
        echo -e "${RED}❌ Opción no válida${NC}"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "✓ Operación completada"
echo "======================================================================"
