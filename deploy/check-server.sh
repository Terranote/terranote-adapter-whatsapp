#!/bin/bash
# Script para verificar el estado del servidor en producción

echo "=== Verificando estado del servidor ==="
echo ""

# Verificar si el servicio systemd está corriendo
echo "1. Verificando servicio systemd..."
if systemctl is-active --quiet terranote-adapter-whatsapp 2>/dev/null; then
    echo "   ✅ Servicio systemd está corriendo"
    systemctl status terranote-adapter-whatsapp --no-pager -l | head -10
else
    echo "   ❌ Servicio systemd NO está corriendo"
fi

echo ""
echo "2. Verificando procesos de uvicorn..."
if pgrep -f "uvicorn.*terranote_adapter_whatsapp" > /dev/null; then
    echo "   ✅ Proceso uvicorn encontrado"
    ps aux | grep uvicorn | grep -v grep
else
    echo "   ❌ No hay proceso uvicorn corriendo"
fi

echo ""
echo "3. Verificando puerto 3001..."
if netstat -tlnp 2>/dev/null | grep -q ":3001 " || ss -tlnp 2>/dev/null | grep -q ":3001 "; then
    echo "   ✅ Puerto 3001 está en uso"
    netstat -tlnp 2>/dev/null | grep ":3001 " || ss -tlnp 2>/dev/null | grep ":3001 "
else
    echo "   ❌ Puerto 3001 NO está en uso"
fi

echo ""
echo "4. Probando health check..."
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo "   ✅ Health check responde correctamente"
    curl -s http://localhost:3001/health
else
    echo "   ❌ Health check NO responde"
fi

echo ""
echo "=== Fin de verificación ==="

