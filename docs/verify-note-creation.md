# Verificar que el Core Crea las Notas Correctamente

## Paso 2: Verificar Creación de Notas en el Core

Después de enviar un mensaje de texto seguido de una ubicación, el core debería crear una nota en OpenStreetMap.

### 2.1. Verificar Logs del Core

```bash
# Ver logs del core en tiempo real
sudo journalctl -u terranote-core -f
```

**Qué buscar en los logs:**

- ✅ `interaction_received` o similar - El core recibió la interacción
- ✅ `note_created` o `creating_note` - El core está creando la nota
- ✅ `note_id` o `note_url` - La nota fue creada exitosamente
- ✅ `callback_sent` o `notifying_adapter` - El core está enviando el callback

### 2.2. Verificar que el Core Procesa las Interacciones

El adaptador envía interacciones al core en `POST /api/v1/interactions`. Verifica que el core las recibe:

```bash
# Ver logs del adaptador para confirmar que envía al core
sudo journalctl -u terranote-adapter-whatsapp -n 20 | grep -E "sending_to_core|core_response_received"
```

Deberías ver:
- `sending_to_core` - El adaptador está enviando
- `core_response_received status_code=200` - El core respondió correctamente

### 2.3. Verificar Respuesta del Core

El core puede responder con diferentes códigos:

- **`200 OK`**: La nota fue creada exitosamente
- **`202 Accepted`**: El core necesita más información (ej: falta ubicación)
- **`400 Bad Request`**: Error en la solicitud
- **`500 Internal Server Error`**: Error del servidor

### 2.4. Verificar en OpenStreetMap (si está configurado)

Si el core está conectado a OpenStreetMap (o un servicio fake), puedes verificar:

1. **Revisar los logs del core** para ver la URL de la nota creada
2. **Visitar la URL** en el navegador para verificar que la nota existe
3. **Verificar en OSM** directamente si tienes acceso

## Flujo Esperado

1. **Usuario envía texto** → Adaptador recibe → Envía al core → Core responde `202 Accepted` (esperando ubicación)
2. **Usuario envía ubicación** → Adaptador recibe → Envía al core → Core crea nota → Core responde `200 OK` con datos de la nota
3. **Core envía callback** → Adaptador recibe → Envía mensaje al usuario con URL de la nota

## Troubleshooting

### El core responde 202 pero no crea la nota

- Verifica que el usuario envió **texto Y ubicación**
- Verifica que la ubicación se envió dentro del tiempo límite (configurado en el core)
- Revisa los logs del core para ver qué está esperando

### El core responde con error

- Revisa los logs del core para ver el error específico
- Verifica la configuración del core (variables de entorno, conexión a OSM, etc.)

### No veo logs de creación de nota

- Verifica que el core está procesando las interacciones
- Revisa si hay errores en los logs del core
- Verifica que el core tiene acceso a OpenStreetMap (o al servicio fake)

