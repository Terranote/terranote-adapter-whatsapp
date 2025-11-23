# Configurar Callback en el Core

## Problema

El core no está enviando callbacks al adaptador de WhatsApp porque no tiene configurado el endpoint.

## Solución

### 1. Agregar Variable de Entorno en el Core

Edita el archivo `.env` del core:

```bash
# En el servidor
nano /home/terranote/terranote-core/.env
```

Agrega o actualiza:

```env
NOTIFIER_WHATSAPP_ENDPOINT=https://terranote-wa.osm.lat/callbacks/note-created
```

**Para desarrollo local:**
```env
NOTIFIER_WHATSAPP_ENDPOINT=http://localhost:3001/callbacks/note-created
```

### 2. Si Usas Firma (Opcional)

Si quieres usar firma para validar los callbacks, configura el mismo token en ambos servicios:

**En el adaptador (`/home/terranote/terranote-adapter-whatsapp/.env`):**
```env
NOTIFIER_SECRET_TOKEN=tu-token-secreto-aqui
```

**En el core (`/home/terranote/terranote-core/.env`):**
```env
NOTIFIER_SECRET_TOKEN=tu-token-secreto-aqui
NOTIFIER_WHATSAPP_ENDPOINT=https://terranote-wa.osm.lat/callbacks/note-created
```

### 3. Reiniciar el Core

Después de actualizar la configuración:

```bash
sudo systemctl restart terranote-core
sudo systemctl status terranote-core
```

### 4. Verificar que Funciona

1. **Envía un mensaje de texto y ubicación** desde WhatsApp
2. **Observa los logs del adaptador:**
   ```bash
   sudo journalctl -u terranote-adapter-whatsapp -f
   ```
3. **Deberías ver:**
   - `notification_sent` - El callback fue recibido y el mensaje enviado a WhatsApp

## Formato del Callback

El core debe enviar un POST al endpoint con este formato:

```json
{
  "channel": "whatsapp",
  "user_id": "573166214032",
  "note_url": "https://www.openstreetmap.org/note/123",
  "note_id": "123",
  "latitude": 4.611,
  "longitude": -74.082,
  "text": "Texto de la nota creada",
  "created_at": "2025-11-23T07:00:00Z"
}
```

## Verificación

Después de configurar, prueba el callback manualmente:

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
    "text": "Test",
    "created_at": "2025-11-23T07:00:00Z"
  }'
```

Debería responder `{"status": "accepted"}` y el usuario debería recibir un mensaje en WhatsApp.

