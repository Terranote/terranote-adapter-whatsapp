# Solucionar Token de WhatsApp Expirado

## Problema

El token de acceso de WhatsApp (`WHATSAPP_ACCESS_TOKEN`) ha expirado. Los logs muestran:

```
Error validating access token: Session has expired on Friday, 21-Nov-25 14:00:00 PST
```

Esto causa que:
- ❌ Los mensajes de bienvenida no se envían (aunque se loguean como enviados)
- ❌ Los callbacks no se pueden enviar al usuario
- ❌ Ningún mensaje sale de WhatsApp

## Solución

### 1. Generar Nuevo Token en Meta Business Suite

1. Ve a [Meta Business Suite](https://business.facebook.com/)
2. Navega a **WhatsApp** → **Tu número** → **API Setup**
3. Busca la sección **"Temporary access token"** o **"Access tokens"**
4. Haz clic en **"Generate new token"** o **"Renew token"**
5. Copia el nuevo token (comienza con `EAA...`)

### 2. Actualizar el Token en el Servidor

```bash
# Conectarse al servidor
ssh angoca@192.168.0.7

# Editar el archivo .env
sudo nano /home/terranote/terranote-adapter-whatsapp/.env
```

Actualiza la línea:
```env
WHATSAPP_ACCESS_TOKEN=TU_NUEVO_TOKEN_AQUI
```

### 3. Reiniciar el Servicio

```bash
sudo systemctl restart terranote-adapter-whatsapp
sudo systemctl status terranote-adapter-whatsapp
```

### 4. Verificar que Funciona

1. **Envía un mensaje nuevo** desde WhatsApp (o borra el usuario de `_seen_users` reiniciando el servicio)
2. **Revisa los logs:**
   ```bash
   sudo journalctl -u terranote-adapter-whatsapp -f
   ```
3. **Deberías ver:**
   - ✅ `welcome_message_sent` (sin errores)
   - ✅ El usuario recibe el mensaje de bienvenida en WhatsApp

## Verificación Rápida

Puedes probar el token manualmente:

```bash
curl -X GET "https://graph.facebook.com/v19.0/864235020113006?access_token=TU_TOKEN_AQUI"
```

Si el token es válido, deberías recibir información del número de teléfono.

## Nota sobre Tokens Permanentes

Los tokens temporales expiran después de ~60 días. Para producción, considera:

1. **Usar tokens de larga duración** (si están disponibles en tu plan)
2. **Implementar renovación automática** usando el API de Meta
3. **Usar System User Access Token** (requiere configuración adicional)

## Confirmación: WhatsApp Cloud API

✅ **Sí, estamos usando WhatsApp Cloud API**. La URL base es:
```
https://graph.facebook.com/v19.0
```

Esta es la API oficial de Meta para WhatsApp Business.

