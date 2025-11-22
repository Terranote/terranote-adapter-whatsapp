#!/bin/bash
# Script para verificar que el flujo de mensajes funciona correctamente

echo "=== Verificación del Flujo de Mensajes ==="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar servidor local
echo "1. Verificando servidor del adaptador..."
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Servidor del adaptador está corriendo${NC}"
else
    echo -e "${RED}❌ Servidor del adaptador NO está corriendo${NC}"
    exit 1
fi

# 2. Verificar configuración del core
echo ""
echo "2. Verificando configuración del core..."
CORE_URL=$(grep CORE_API_BASE_URL /home/terranote/terranote-adapter-whatsapp/.env 2>/dev/null | cut -d'=' -f2)
if [ -z "$CORE_URL" ]; then
    echo -e "${RED}❌ CORE_API_BASE_URL no está configurado${NC}"
else
    echo -e "${GREEN}✅ CORE_API_BASE_URL: $CORE_URL${NC}"
    
    # 3. Verificar conectividad al core
    echo ""
    echo "3. Verificando conectividad al core..."
    if curl -s --connect-timeout 5 "$CORE_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Core está accesible${NC}"
    else
        echo -e "${YELLOW}⚠️  Core no responde (puede ser normal si no está corriendo)${NC}"
    fi
fi

# 4. Verificar proceso uvicorn
echo ""
echo "4. Verificando proceso del servidor..."
if pgrep -f "uvicorn.*terranote_adapter_whatsapp" > /dev/null; then
    echo -e "${GREEN}✅ Proceso uvicorn está corriendo${NC}"
    ps aux | grep "uvicorn.*terranote" | grep -v grep | head -1
else
    echo -e "${RED}❌ Proceso uvicorn NO está corriendo${NC}"
fi

# 5. Verificar webhook
echo ""
echo "5. Verificando webhook..."
WEBHOOK_RESPONSE=$(curl -s "http://localhost:3001/webhook?hub.mode=subscribe&hub.challenge=test&hub.verify_token=$(grep WHATSAPP_VERIFY_TOKEN /home/terranote/terranote-adapter-whatsapp/.env 2>/dev/null | cut -d'=' -f2)")
if [ "$WEBHOOK_RESPONSE" = "test" ]; then
    echo -e "${GREEN}✅ Webhook responde correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Webhook no responde como se espera: $WEBHOOK_RESPONSE${NC}"
fi

# 6. Mostrar últimos logs (si están disponibles)
echo ""
echo "6. Últimos logs (si el servidor está como servicio systemd):"
if systemctl is-active --quiet terranote-adapter-whatsapp 2>/dev/null; then
    journalctl -u terranote-adapter-whatsapp -n 5 --no-pager 2>/dev/null || echo "No hay logs recientes"
else
    echo "El servidor no está corriendo como servicio systemd"
    echo "Si está corriendo manualmente, revisa la terminal donde lo ejecutaste"
fi

echo ""
echo "=== Para ver logs en tiempo real: ==="
echo "Si está como servicio: sudo journalctl -u terranote-adapter-whatsapp -f"
echo "Si está manual: revisa la terminal donde ejecutaste uvicorn"
echo ""
echo "=== Para probar enviando un mensaje: ==="
echo "1. Envía un mensaje de WhatsApp al número de prueba"
echo "2. Observa los logs para ver:"
echo "   - 'interaction_forwarded' = mensaje enviado al core exitosamente"
echo "   - 'core_rejected_interaction' = el core rechazó el mensaje"
echo "   - 'core_unreachable' = no se puede alcanzar el core"

