# Probar el Mensaje de Bienvenida

## Paso 1: Reiniciar el Servicio

Para limpiar la lista de usuarios vistos (`_seen_users`) y probar el mensaje de bienvenida:

```bash
# Reiniciar el servicio (esto limpia _seen_users)
sudo systemctl restart terranote-adapter-whatsapp

# Verificar que está corriendo
sudo systemctl status terranote-adapter-whatsapp
curl http://localhost:3001/health
```

## Paso 2: Enviar un Mensaje desde WhatsApp

1. **Abre WhatsApp** en tu teléfono
2. **Envía un mensaje** al número configurado (el número de WhatsApp Business)
3. **Deberías recibir automáticamente** el mensaje de bienvenida con botones

## Paso 3: Verificar los Logs

Mientras envías el mensaje, observa los logs:

```bash
sudo journalctl -u terranote-adapter-whatsapp -f
```

**Logs que deberías ver:**

✅ `webhook_received` - Facebook envió el mensaje
✅ `processing_message` - El adaptador está procesando
✅ `welcome_message_sent` - **Este es el importante** - Confirma que se envió la bienvenida
✅ `sending_to_core` - Se envía al core
✅ `core_response_received` - El core respondió
✅ `interaction_forwarded` - Todo exitoso

## Qué Esperar

### Mensaje de Bienvenida en Español:

```
¡Hola! 👋 Bienvenido a *Terranote*.

Puedes crear notas enviándome un mensaje de texto y luego tu ubicación.

¿Cómo puedo ayudarte?

[Botones: Crear nota | Ver ayuda | Más info]
```

### Mensaje de Bienvenida en Inglés:

```
Hello! 👋 Welcome to *Terranote*.

You can create notes by sending me a text message and then your location.

How can I help you?

[Buttons: Create note | Help | More info]
```

## Notas Importantes

- El mensaje de bienvenida **solo se envía la primera vez** que un usuario envía un mensaje
- Después de reiniciar el servicio, la lista `_seen_users` se limpia, así que el próximo mensaje de cualquier usuario activará la bienvenida
- Si no ves `welcome_message_sent` en los logs, puede haber un error al enviar el mensaje (revisa `failed_to_send_welcome`)

## Troubleshooting

### No recibo el mensaje de bienvenida

1. **Verifica los logs:**
   ```bash
   sudo journalctl -u terranote-adapter-whatsapp -n 50 | grep -i "welcome\|failed"
   ```

2. **Verifica el token de WhatsApp:**
   - El `WHATSAPP_ACCESS_TOKEN` puede haber expirado
   - Genera uno nuevo en Meta Business Suite si es necesario

3. **Verifica que el usuario es nuevo:**
   - Si el usuario ya envió mensajes antes del reinicio, puede que ya esté en la lista
   - Prueba con un número de WhatsApp diferente

### Veo `failed_to_send_welcome` en los logs

Esto significa que hubo un error al enviar el mensaje de bienvenida. Posibles causas:
- Token de acceso expirado
- `WHATSAPP_PHONE_NUMBER_ID` incorrecto
- Problemas de conectividad con la API de WhatsApp

Revisa los logs para ver el error específico.

