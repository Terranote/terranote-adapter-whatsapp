# Cómo Ver los Logs del Adaptador

## Situación Actual

El servidor está corriendo **manualmente** (no como servicio systemd), por lo que los logs aparecen directamente en la terminal donde lo ejecutaste.

## Dónde Ver los Logs

### Opción 1: Terminal donde ejecutaste el servidor

Si ejecutaste el servidor con:
```bash
uvicorn terranote_adapter_whatsapp.main:app --host 0.0.0.0 --port 3001
```

Los logs aparecen **directamente en esa terminal**. Cada vez que:
- Recibes un mensaje de WhatsApp
- Envías un mensaje al core
- Hay un error

Verás mensajes como:
```
INFO: webhook_received event_object=whatsapp_business_account entries_count=1
INFO: processing_change field=messages messages_count=1
INFO: processing_message message_id=wamid.xxx message_type=text from_user=573000000000
INFO: interaction_created user_id=573000000000 channel=whatsapp
INFO: sending_to_core user_id=573000000000 core_url=https://terranote-core.local
INFO: core_response_received status_code=202 user_id=573000000000
INFO: interaction_forwarded user_id=573000000000 message_id=wamid.xxx
```

### Opción 2: Si no tienes acceso a esa terminal

Si ejecutaste el servidor en segundo plano o perdiste la terminal, puedes:

1. **Encontrar el proceso:**
   ```bash
   ps aux | grep uvicorn | grep terranote
   ```

2. **Ver los logs del proceso** (si está corriendo con redirección):
   ```bash
   # Si lo ejecutaste con nohup o redirección
   tail -f /home/terranote/terranote-adapter-whatsapp/logs/*.log
   ```

3. **Reiniciar el servidor en una terminal que puedas ver:**
   ```bash
   # Detener el proceso actual
   pkill -f "uvicorn.*terranote_adapter_whatsapp"
   
   # Iniciar en una nueva terminal (o con screen/tmux)
   sudo su - terranote
   cd /home/terranote/terranote-adapter-whatsapp
   source .venv/bin/activate
   uvicorn terranote_adapter_whatsapp.main:app --host 0.0.0.0 --port 3001
   ```

## Qué Logs Verás Ahora

Con el logging adicional que agregamos, cuando recibas un mensaje verás:

1. **`webhook_received`** - Facebook envió un evento al webhook
2. **`processing_change`** - Procesando un cambio (campo `messages`)
3. **`processing_message`** - Procesando un mensaje específico
4. **`interaction_created`** - Mensaje convertido a interacción
5. **`sending_to_core`** - Enviando al core (con la URL)
6. **`core_response_received`** - Respuesta del core (con código de estado)
7. **`interaction_forwarded`** - Todo exitoso ✅

Si hay errores, verás:
- **`core_rejected_interaction`** - El core rechazó el mensaje
- **`core_unreachable`** - No se puede alcanzar el core
- **`unsupported_message`** - Tipo de mensaje no soportado

## Probar Ahora

1. **Asegúrate de tener acceso a la terminal donde corre el servidor**
2. **Envía un mensaje de WhatsApp** al número de prueba
3. **Observa los logs** en la terminal
4. **Verifica que veas todos los pasos** desde `webhook_received` hasta `interaction_forwarded`

## Si No Ves Logs

Si no ves logs cuando envías un mensaje:

1. Verifica que el servidor esté corriendo:
   ```bash
   ps aux | grep uvicorn | grep terranote
   ```

2. Verifica que el webhook esté verificado en Facebook

3. Verifica que el evento `messages` esté suscrito en Facebook

4. Revisa los logs de Facebook (en el dashboard) para ver si hay errores

