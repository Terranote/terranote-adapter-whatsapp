# Solución: Core No Accesible

## Problema

Los logs muestran:
```
core_unreachable error=All connection attempts failed
```

El adaptador intenta conectarse a `http://localhost:3002` pero el core no está disponible en ese puerto.

## Solución 1: Iniciar el servicio del core (Recomendado)

El servicio systemd del core debería estar corriendo en el puerto 3002:

```bash
# En el servidor
sudo systemctl start terranote-core
sudo systemctl status terranote-core
```

Verifica que esté corriendo:
```bash
curl http://localhost:3002/health
```

## Solución 2: Usar el core manual temporalmente

Si el core está corriendo manualmente en el puerto 8002, puedes cambiar temporalmente la configuración:

```bash
# Editar .env del adaptador
cd /home/terranote/terranote-adapter-whatsapp
nano .env

# Cambiar:
# CORE_API_BASE_URL=http://localhost:8002

# Reiniciar el servicio
sudo systemctl restart terranote-adapter-whatsapp
```

## Verificar

Después de aplicar la solución, envía un mensaje desde WhatsApp y verifica los logs:

```bash
sudo journalctl -u terranote-adapter-whatsapp -f
```

Deberías ver:
- ✅ `sending_to_core` sin errores
- ✅ `core_response_received` con status 200 o 202
- ❌ Ya no debería aparecer `core_unreachable`

