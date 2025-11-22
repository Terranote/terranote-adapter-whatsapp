#!/bin/bash
# Script para verificar que el servidor está bien configurado

echo "=== Verificación del Servidor WhatsApp Adapter ==="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Verificar si el proceso está corriendo
echo "1. Verificando proceso del servidor..."
if pgrep -f "uvicorn.*terranote_adapter_whatsapp" > /dev/null; then
    echo -e "   ${GREEN}✅ Servidor está corriendo${NC}"
    ps aux | grep uvicorn | grep terranote | grep -v grep
else
    echo -e "   ${RED}❌ Servidor NO está corriendo${NC}"
fi

echo ""

# 2. Verificar puerto 3001
echo "2. Verificando puerto 3001..."
if netstat -tlnp 2>/dev/null | grep -q ":3001 " || ss -tlnp 2>/dev/null | grep -q ":3001 "; then
    echo -e "   ${GREEN}✅ Puerto 3001 está en uso${NC}"
    netstat -tlnp 2>/dev/null | grep ":3001 " || ss -tlnp 2>/dev/null | grep ":3001 "
else
    echo -e "   ${RED}❌ Puerto 3001 NO está en uso${NC}"
fi

echo ""

# 3. Verificar health check
echo "3. Verificando health check..."
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Health check responde correctamente${NC}"
    RESPONSE=$(curl -s http://localhost:3001/health)
    echo "   Respuesta: $RESPONSE"
else
    echo -e "   ${RED}❌ Health check NO responde${NC}"
fi

echo ""

# 4. Verificar .env
echo "4. Verificando archivo .env..."
ENV_FILE="/home/terranote/terranote-adapter-whatsapp/.env"
if [ -f "$ENV_FILE" ]; then
    echo -e "   ${GREEN}✅ Archivo .env existe${NC}"
    
    # Verificar variables importantes
    if grep -q "WHATSAPP_ACCESS_TOKEN=" "$ENV_FILE" && ! grep -q "WHATSAPP_ACCESS_TOKEN=replace-me" "$ENV_FILE"; then
        echo -e "   ${GREEN}✅ WHATSAPP_ACCESS_TOKEN configurado${NC}"
    else
        echo -e "   ${YELLOW}⚠️  WHATSAPP_ACCESS_TOKEN no configurado o es placeholder${NC}"
    fi
    
    if grep -q "WHATSAPP_PHONE_NUMBER_ID=" "$ENV_FILE" && ! grep -q "WHATSAPP_PHONE_NUMBER_ID=replace-me" "$ENV_FILE"; then
        echo -e "   ${GREEN}✅ WHATSAPP_PHONE_NUMBER_ID configurado${NC}"
        PHONE_ID=$(grep "WHATSAPP_PHONE_NUMBER_ID=" "$ENV_FILE" | cut -d'=' -f2)
        echo "   Valor: $PHONE_ID"
    else
        echo -e "   ${YELLOW}⚠️  WHATSAPP_PHONE_NUMBER_ID no configurado o es placeholder${NC}"
    fi
    
    if grep -q "WHATSAPP_VERIFY_TOKEN=" "$ENV_FILE" && ! grep -q "WHATSAPP_VERIFY_TOKEN=replace-me" "$ENV_FILE"; then
        echo -e "   ${GREEN}✅ WHATSAPP_VERIFY_TOKEN configurado${NC}"
    else
        echo -e "   ${YELLOW}⚠️  WHATSAPP_VERIFY_TOKEN no configurado o es placeholder${NC}"
    fi
else
    echo -e "   ${RED}❌ Archivo .env NO existe${NC}"
fi

echo ""

# 5. Verificar cloudflared (si está corriendo)
echo "5. Verificando cloudflared..."
if pgrep -f cloudflared > /dev/null; then
    echo -e "   ${GREEN}✅ Cloudflared está corriendo${NC}"
    ps aux | grep cloudflared | grep -v grep | head -1
    echo ""
    echo "   ${YELLOW}⚠️  Nota: Verifica la URL de cloudflared para usar en Facebook${NC}"
else
    echo -e "   ${YELLOW}⚠️  Cloudflared NO está corriendo${NC}"
    echo "   Si necesitas exponer el servidor, ejecuta: cloudflared tunnel --url http://localhost:3001"
fi

echo ""

# 6. Verificar servicio systemd
echo "6. Verificando servicio systemd..."
if systemctl list-unit-files | grep -q "terranote-adapter-whatsapp.service"; then
    if systemctl is-active --quiet terranote-adapter-whatsapp 2>/dev/null; then
        echo -e "   ${GREEN}✅ Servicio systemd está activo${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Servicio systemd existe pero NO está activo${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  Servicio systemd NO está instalado${NC}"
fi

echo ""
echo "=== Fin de verificación ==="
echo ""

# Resumen
echo "📋 Resumen:"
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Servidor está funcionando${NC}"
    echo ""
    echo "📝 Próximos pasos:"
    echo "   1. Si cloudflared está corriendo, copia la URL y agrega /webhook al final"
    echo "   2. Ve a Facebook Developers → Tu app → WhatsApp → Configuration → Webhooks"
    echo "   3. Configura:"
    echo "      - Callback URL: https://tu-url-cloudflared/webhook"
    echo "      - Verify token: (el que está en tu .env)"
    echo "   4. Haz clic en 'Verify and save'"
    echo "   5. Marca 'messages' y 'message_reactions'"
else
    echo -e "   ${RED}❌ Servidor NO está funcionando correctamente${NC}"
    echo ""
    echo "🔧 Acciones necesarias:"
    echo "   1. Iniciar el servidor (como usuario terranote)"
    echo "   2. Verificar que el .env esté configurado correctamente"
fi

