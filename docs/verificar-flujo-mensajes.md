# Verificar que se Reciben Mensajes y se Envían al Core

Esta guía te ayuda a verificar que el adaptador está recibiendo mensajes de WhatsApp y enviándolos correctamente al core.

## Métodos de Verificación

### 1. Ver los Logs del Servidor (Tiempo Real)

Si el servidor está corriendo manualmente, los logs aparecen directamente en la terminal. Si está como servicio systemd:

```bash
# Ver logs en tiempo real
sudo journalctl -u terranote-adapter-whatsapp -f

# O si está corriendo manualmente, los logs aparecen en la terminal donde lo ejecutaste
```

**Logs que debes ver cuando funciona:**

- ✅ `interaction_forwarded` - Mensaje recibido y enviado al core exitosamente
- ⚠️ `unsupported_message` - Mensaje recibido pero tipo no soportado (se ignora)
- ❌ `core_rejected_interaction` - El core rechazó el mensaje
- ❌ `core_unreachable` - No se puede alcanzar el core

### 2. Verificar que el Core está Accesible

```bash
# Verificar la URL del core configurada
ssh angoca@192.168.0.7 "cat /home/terranote/terranote-adapter-whatsapp/.env | grep CORE_API_BASE_URL"

# Probar conectividad al core
curl https://terranote-core.local/api/v1/interactions
# O la URL que tengas configurada
```

### 3. Agregar Logging Adicional (Temporal para Debug)

Puedes agregar logging temporal para ver más detalles. Edita `src/terranote_adapter_whatsapp/routes/webhook.py`:

```python
@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(
    event: WebhookEvent,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, int | str]:
    """Handle incoming WhatsApp events from Meta."""
    # Agregar logging del evento recibido
    logger.info("webhook_received", event_object=event.object, entries_count=len(event.entry))
    
    processor = MessageProcessor()
    core_client = TerranoteCoreClient(settings)

    processed = 0
    for entry in event.entry:
        for change in entry.changes:
            logger.info("processing_change", field=change.field, messages_count=len(change.value.messages))
            
            for message in change.value.messages:
                logger.info("processing_message", 
                          message_id=message.id, 
                          message_type=message.type,
                          from_user=message.from_)
                
                try:
                    interaction = processor.to_interaction(user_id=message.from_, message=message)
                    logger.info("interaction_created", 
                              user_id=interaction.user_id,
                              channel=interaction.channel,
                              payload_type=type(interaction.payload).__name__)
                except ValueError as exc:
                    # ... código existente ...
```

### 4. Verificar con un Mensaje de Prueba

1. **Envía un mensaje de WhatsApp** al número de prueba
2. **Observa los logs** en tiempo real
3. **Verifica en el core** que recibió la interacción

### 5. Verificar el Core Recibió el Mensaje

Revisa los logs del core para confirmar que recibió la petición:

```bash
# Si el core está en el mismo servidor
ssh angoca@192.168.0.7 "sudo journalctl -u terranote-core -f"

# O revisa los logs del core según cómo esté configurado
```

### 6. Probar Manualmente el Endpoint del Core

Puedes probar enviar una interacción manualmente al core:

```bash
curl -X POST https://terranote-core.local/api/v1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "whatsapp",
    "user_id": "573000000000",
    "sent_at": "2025-11-22T15:00:00Z",
    "payload": {
      "type": "text",
      "text": "Mensaje de prueba"
    }
  }'
```

## Problemas Comunes

### El servidor no recibe mensajes

- Verifica que el webhook esté verificado en Facebook
- Verifica que el evento `messages` esté suscrito
- Revisa los logs de Facebook para ver si hay errores

### El core no recibe los mensajes

- Verifica que `CORE_API_BASE_URL` esté correcto
- Verifica que el core esté accesible desde el servidor
- Revisa los logs del adaptador para ver errores de conexión

### Los mensajes se reciben pero no se procesan

- Verifica que el tipo de mensaje sea `text` o `location`
- Revisa los logs para ver si hay `unsupported_message`

## Script de Verificación Rápida

Crea un script `verify-flow.sh`:

```bash
#!/bin/bash
echo "=== Verificación del Flujo de Mensajes ==="
echo ""
echo "1. Verificando servidor..."
curl -s http://localhost:3001/health && echo " ✅" || echo " ❌"
echo ""
echo "2. Verificando core..."
curl -s $CORE_API_BASE_URL/health && echo " ✅" || echo " ❌"
echo ""
echo "3. Últimos logs del adaptador:"
journalctl -u terranote-adapter-whatsapp -n 10 --no-pager 2>/dev/null || echo "No hay logs del servicio"
```

