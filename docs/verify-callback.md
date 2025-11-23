# Verificar que el Callback de Nota Creada Funciona

## Paso 3: Verificar el Callback

Después de que el core crea una nota, debe enviar un callback al adaptador para notificar al usuario en WhatsApp.

### 3.1. Verificar Configuración del Core

El core debe tener configurado el endpoint del adaptador para enviar callbacks:

```bash
# Verificar variables de entorno del core
grep NOTIFIER /home/terranote/terranote-core/.env
```

Debería tener algo como:
```env
NOTIFIER_WHATSAPP_ENDPOINT=https://terranote-wa.osm.lat/callbacks/note-created
# o para desarrollo local:
NOTIFIER_WHATSAPP_ENDPOINT=http://localhost:3001/callbacks/note-created
```

### 3.2. Probar el Callback Manualmente

Puedes probar el endpoint de callback directamente:

```bash
curl -X POST http://localhost:3001/callbacks/note-created \
  -H 'Content-Type: application/json' \
  -d '{
    "channel": "whatsapp",
    "user_id": "573166214032",
    "note_url": "https://www.openstreetmap.org/note/123",
    "note_id": "123",
    "latitude": 4.611,
    "longitude": -74.082,
    "text": "Nota de prueba",
    "created_at": "2025-11-23T07:00:00Z"
  }'
```

**Respuesta esperada:**
```json
{"status": "accepted"}
```

**Logs que deberías ver:**
- `notification_sent` - El mensaje fue enviado a WhatsApp

### 3.3. Verificar Logs del Adaptador

Cuando el core envía un callback, deberías ver en los logs:

```bash
sudo journalctl -u terranote-adapter-whatsapp -f
```

**Logs esperados:**
- `notification_sent` - El callback fue procesado y el mensaje enviado a WhatsApp
- O `whatsapp_rejected_message` si hay un error al enviar

### 3.4. Verificar que el Core Envía Callbacks

Revisa los logs del core para ver si está intentando enviar callbacks:

```bash
sudo journalctl -u terranote-core -f | grep -i "callback\|notifier\|note.*created"
```

### 3.5. Flujo Completo Esperado

1. **Usuario envía texto** → Adaptador → Core (responde `202 Accepted`, esperando ubicación)
2. **Usuario envía ubicación** → Adaptador → Core (responde `200 OK`, nota creada)
3. **Core envía callback** → Adaptador recibe → Adaptador envía mensaje a WhatsApp
4. **Usuario recibe mensaje** en WhatsApp con la URL de la nota

## Troubleshooting

### No veo callbacks en los logs

**Posibles causas:**
1. El core no está configurado para enviar callbacks
2. El endpoint del callback no es accesible desde el core
3. El core no está creando notas (solo está recibiendo interacciones)

**Solución:**
- Verifica la configuración `NOTIFIER_WHATSAPP_ENDPOINT` en el core
- Verifica que el adaptador sea accesible desde el core
- Revisa los logs del core para ver si hay errores al enviar callbacks

### El callback falla con error 401

**Causa:** El adaptador está configurado para requerir firma (`NOTIFIER_SECRET_TOKEN`) pero el core no la está enviando.

**Solución:**
- Verifica que `NOTIFIER_SECRET_TOKEN` esté configurado igual en ambos servicios
- O desactiva la verificación de firma temporalmente para pruebas

### El callback llega pero no se envía el mensaje a WhatsApp

**Causa:** Error al enviar el mensaje a WhatsApp (token expirado, etc.)

**Solución:**
- Revisa los logs para ver el error específico
- Verifica que `WHATSAPP_ACCESS_TOKEN` sea válido
- Verifica que `WHATSAPP_PHONE_NUMBER_ID` sea correcto

