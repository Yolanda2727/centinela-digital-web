#!/bin/bash
# Script para ejecutar las pruebas en orden: Suite completa, API, y Cliente

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           🧪 EJECUTOR COMPLETO DE PRUEBAS CENTINELA DIGITAL 🧪     ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paso 1: Suite de validación completa
echo -e "${YELLOW}📊 PASO 1: Ejecutando suite de validación (tests, BD, API)...${NC}"
echo "════════════════════════════════════════════════════════════════════"
python3 run_tests.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Suite de validación falló${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Suite de validación completada${NC}"
echo ""

# Paso 2: Explicar cómo iniciar la API
echo -e "${YELLOW}🌐 PASO 2: Iniciando API REST...${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo "Para probar los endpoints, en otra terminal ejecuta:"
echo "  python3 run_api.sh"
echo ""
echo "Luego, en una tercera terminal:"
echo "  python3 test_api_endpoints.py"
echo ""

# Paso 3: Ofrecer opciones
echo -e "${YELLOW}💡 OPCIONES DISPONIBLES:${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  API REST (Backend)"
echo "   Comando: python3 run_api.sh"
echo "   Puerto: 5000"
echo "   Uso: para integración con sistemas externos"
echo ""
echo "2️⃣  Aplicación Web (Frontend - Streamlit)"
echo "   Comando: streamlit run app.py"
echo "   Puerto: 8501"
echo "   Uso: interfaz gráfica para análisis interactivo"
echo ""
echo "3️⃣  Cliente API Python"
echo "   Comando: python3 api_client.py"
echo "   Uso: script para consumir la API desde Python"
echo ""
echo "4️⃣  Pruebas de Endpoints"
echo "   Comando: python3 test_api_endpoints.py"
echo "   Requisito: API debe estar corriendo (step 1)"
echo ""

echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ VALIDACIÓN COMPLETADA - LISTO PARA USAR${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
