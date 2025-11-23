# Solución: Servicio del Core No Responde

## Problema

El servicio `terranote-core` aparece como "active running" pero no responde en el puerto 3002.

## Diagnóstico

```bash
# Verificar estado del servicio
sudo systemctl status terranote-core

# Ver logs del servicio
sudo journalctl -u terranote-core -n 50

# Verificar si hay algo escuchando en el puerto
netstat -tlnp | grep 3002
# o
ss -tlnp | grep 3002
```

## Soluciones

### Solución 1: Reiniciar el servicio del core

```bash
# Detener el servicio
sudo systemctl stop terranote-core

# Verificar que no hay procesos manuales corriendo
ps aux | grep "uvicorn.*core" | grep -v grep

# Si hay procesos manuales, detenerlos
kill <PID>

# Iniciar el servicio
sudo systemctl start terranote-core

# Verificar que está corriendo
sudo systemctl status terranote-core
curl http://localhost:3002/health
```

### Solución 2: Verificar configuración del servicio

El servicio debería estar configurado para usar el puerto 3002:

```bash
# Ver la configuración del servicio
cat /etc/systemd/system/terranote-core.service | grep ExecStart
```

Debería mostrar:
```
ExecStart=/home/terranote/.local/bin/poetry run uvicorn app.main:app --host 127.0.0.1 --port 3002
```

### Solución 3: Verificar logs de errores

```bash
# Ver logs recientes
sudo journalctl -u terranote-core -n 100 --no-pager

# Buscar errores
sudo journalctl -u terranote-core -n 100 | grep -i error
```

Posibles errores:
- Error de permisos
- Puerto ya en uso
- Error en el código del core
- Variables de entorno faltantes

### Solución 4: Verificar que el core tiene el endpoint /health

El core debe tener un endpoint `/health` que responda. Si no lo tiene, el adaptador no podrá verificar la conexión.

## Verificación Final

Después de aplicar la solución:

```bash
# 1. Verificar que el servicio está corriendo
sudo systemctl status terranote-core

# 2. Verificar que responde en el puerto 3002
curl http://localhost:3002/health

# 3. Verificar logs del adaptador
sudo journalctl -u terranote-adapter-whatsapp -f
```

Deberías ver en los logs del adaptador:
- ✅ `sending_to_core` sin errores
- ✅ `core_response_received` con status 200 o 202
- ❌ Ya no debería aparecer `core_unreachable`

