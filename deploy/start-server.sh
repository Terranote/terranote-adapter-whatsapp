#!/bin/bash
# Script para iniciar el servidor en producción

REPO_DIR="/home/terranote/terranote-adapter-whatsapp"

echo "=== Iniciando servidor WhatsApp Adapter ==="
echo ""

# Verificar si el servicio systemd existe
if systemctl list-unit-files | grep -q "terranote-adapter-whatsapp.service"; then
    echo "1. Iniciando servicio systemd..."
    sudo systemctl start terranote-adapter-whatsapp
    sleep 2
    if systemctl is-active --quiet terranote-adapter-whatsapp; then
        echo "   ✅ Servicio iniciado correctamente"
        systemctl status terranote-adapter-whatsapp --no-pager -l | head -5
    else
        echo "   ❌ Error al iniciar el servicio"
        echo "   Revisa los logs: sudo journalctl -u terranote-adapter-whatsapp -n 20"
    fi
else
    echo "1. Servicio systemd no encontrado. Iniciando manualmente..."
    
    if [ ! -d "$REPO_DIR" ]; then
        echo "   ❌ Error: Repositorio no encontrado en $REPO_DIR"
        exit 1
    fi
    
    cd "$REPO_DIR"
    
    if [ ! -d ".venv" ]; then
        echo "   ⚠️  Virtualenv no encontrado. Ejecuta primero: ./deploy/setup-local.sh"
        exit 1
    fi
    
    echo "   Iniciando servidor en puerto 3001..."
    source .venv/bin/activate
    nohup uvicorn terranote_adapter_whatsapp.main:app --host 0.0.0.0 --port 3001 --no-reload > logs/server.log 2>&1 &
    
    sleep 2
    
    if pgrep -f "uvicorn.*terranote_adapter_whatsapp" > /dev/null; then
        echo "   ✅ Servidor iniciado correctamente"
        echo "   PID: $(pgrep -f 'uvicorn.*terranote_adapter_whatsapp')"
    else
        echo "   ❌ Error al iniciar el servidor"
        echo "   Revisa los logs: tail -f $REPO_DIR/logs/server.log"
    fi
fi

echo ""
echo "2. Verificando que responda..."
sleep 1
if curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo "   ✅ Servidor responde correctamente"
    curl -s http://localhost:3001/health
else
    echo "   ❌ Servidor no responde aún"
    echo "   Espera unos segundos y prueba: curl http://localhost:3001/health"
fi

echo ""
echo "=== Fin ==="

