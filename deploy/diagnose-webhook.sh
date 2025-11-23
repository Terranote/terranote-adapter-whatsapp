#!/usr/bin/env bash
# Script para diagnosticar problemas con el webhook de WhatsApp

set -euo pipefail

echo "=== Diagnóstico del Webhook de WhatsApp ==="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que el servicio está corriendo
echo -e "${YELLOW}1. Verificando servicio...${NC}"
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Servicio respondiendo en puerto 3001${NC}"
else
    echo -e "${RED}✗ Servicio NO responde en puerto 3001${NC}"
    exit 1
fi

# 2. Verificar variables de entorno
echo -e "${YELLOW}2. Verificando configuración...${NC}"
if [ -f /home/terranote/terranote-adapter-whatsapp/.env ]; then
    echo -e "${GREEN}✓ Archivo .env existe${NC}"
    
    if grep -q "WHATSAPP_ACCESS_TOKEN" /home/terranote/terranote-adapter-whatsapp/.env; then
        TOKEN=$(grep "WHATSAPP_ACCESS_TOKEN" /home/terranote/terranote-adapter-whatsapp/.env | cut -d'=' -f2)
        if [ ${#TOKEN} -gt 50 ]; then
            echo -e "${GREEN}✓ Access Token configurado (${#TOKEN} caracteres)${NC}"
        else
            echo -e "${RED}✗ Access Token parece inválido${NC}"
        fi
    else
        echo -e "${RED}✗ Access Token no encontrado${NC}"
    fi
    
    if grep -q "WHATSAPP_PHONE_NUMBER_ID" /home/terranote/terranote-adapter-whatsapp/.env; then
        PHONE_ID=$(grep "WHATSAPP_PHONE_NUMBER_ID" /home/terranote/terranote-adapter-whatsapp/.env | cut -d'=' -f2)
        echo -e "${GREEN}✓ Phone Number ID: $PHONE_ID${NC}"
    else
        echo -e "${RED}✗ Phone Number ID no encontrado${NC}"
    fi
else
    echo -e "${RED}✗ Archivo .env no existe${NC}"
fi

# 3. Verificar que el webhook responde
echo -e "${YELLOW}3. Probando endpoint del webhook...${NC}"
TEST_PAYLOAD='{"object":"whatsapp_business_account","entry":[{"id":"test","changes":[{"field":"messages","value":{"messaging_product":"whatsapp","metadata":{},"messages":[{"from":"573000000000","id":"test123","timestamp":"1734567890","type":"text","text":{"body":"test"}}]}}]}]}'

RESPONSE=$(curl -s -X POST http://localhost:3001/webhook \
    -H 'Content-Type: application/json' \
    -d "$TEST_PAYLOAD" 2>&1)

if echo "$RESPONSE" | grep -q "accepted\|processed"; then
    echo -e "${GREEN}✓ Webhook responde correctamente${NC}"
    echo "   Respuesta: $RESPONSE"
else
    echo -e "${YELLOW}⚠ Webhook responde pero con error:${NC}"
    echo "   $RESPONSE"
fi

# 4. Verificar logs recientes
echo -e "${YELLOW}4. Últimos logs del servicio (si disponible)...${NC}"
if command -v journalctl > /dev/null 2>&1; then
    echo "   (Ejecuta 'sudo journalctl -u terranote-adapter-whatsapp -n 50 -f' para ver logs en tiempo real)"
else
    echo "   journalctl no disponible"
fi

# 5. Verificar conectividad con el core
echo -e "${YELLOW}5. Verificando conectividad con el core...${NC}"
CORE_URL=$(grep "CORE_API_BASE_URL" /home/terranote/terranote-adapter-whatsapp/.env 2>/dev/null | cut -d'=' -f2 || echo "http://localhost:3002")

if curl -s "$CORE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Core accesible en $CORE_URL${NC}"
else
    echo -e "${YELLOW}⚠ Core NO accesible en $CORE_URL${NC}"
    echo "   (Esto es normal si el endpoint de ayuda no está implementado aún)"
fi

echo ""
echo -e "${YELLOW}=== Verificaciones Adicionales ===${NC}"
echo ""
echo "Para verificar si Facebook está enviando mensajes:"
echo "  1. Verifica la configuración del webhook en Meta Business Suite"
echo "  2. Asegúrate de que la URL del webhook sea accesible desde internet"
echo "  3. Verifica que el dominio esté correctamente configurado (terranote-wa.osm.lat)"
echo ""
echo "Para ver logs en tiempo real:"
echo "  sudo journalctl -u terranote-adapter-whatsapp -f"
echo ""
echo "Para probar el webhook manualmente:"
echo "  curl -X POST http://localhost:3001/webhook -H 'Content-Type: application/json' -d @test-payload.json"

