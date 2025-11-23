# Troubleshooting: El Webhook No Recibe Mensajes

Si envías un mensaje desde WhatsApp y no pasa nada, sigue estos pasos para diagnosticar el problema.

## 🔍 Diagnóstico Rápido

### 1. Verificar que el servicio está corriendo

```bash
curl http://localhost:3001/health
```

Debería responder: `{"status":"ok"}`

### 2. Verificar que el webhook es accesible desde internet

```bash
# Desde tu máquina local o cualquier lugar con internet
curl https://terranote-wa.osm.lat/health
```

Si no responde, el problema es que el webhook no es accesible desde internet.

### 3. Verificar la configuración en Facebook

1. Ve a [Meta Business Suite](https://business.facebook.com/)
2. Navega a **WhatsApp** → Tu número → **Configuration** → **Webhooks**
3. Verifica que:
   - ✅ La **Callback URL** sea: `https://terranote-wa.osm.lat/webhook`
   - ✅ El **Verify token** sea: `PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8`
   - ✅ El webhook esté **verificado** (debe mostrar un ✅ verde)
   - ✅ Estés suscrito al campo **`messages`**

### 4. Verificar logs del servicio

```bash
# En el servidor
sudo journalctl -u terranote-adapter-whatsapp -f
```

Luego envía un mensaje desde WhatsApp y observa si aparecen logs como:
- `webhook_received`
- `processing_message`
- `welcome_message_sent`

## 🐛 Problemas Comunes

### Problema 1: No aparecen logs cuando envías un mensaje

**Causa:** Facebook no está enviando los mensajes al webhook.

**Solución:**
1. Verifica que el webhook esté **verificado** en Facebook (debe mostrar ✅)
2. Verifica que estés suscrito al campo **`messages`**
3. Verifica que la URL del webhook sea accesible desde internet
4. Verifica que el dominio `terranote-wa.osm.lat` esté correctamente configurado

### Problema 2: Aparecen logs pero no se envía el mensaje de bienvenida

**Causa:** Error al enviar el mensaje de bienvenida a WhatsApp.

**Solución:**
1. Verifica los logs para ver el error específico:
   ```bash
   sudo journalctl -u terranote-adapter-whatsapp -n 50 | grep -i "welcome\|error"
   ```
2. Verifica que `WHATSAPP_ACCESS_TOKEN` sea válido y no haya expirado
3. Verifica que `WHATSAPP_PHONE_NUMBER_ID` sea correcto

### Problema 3: El webhook no es accesible desde internet

**Causa:** El túnel de Cloudflare o la configuración DNS no está funcionando.

**Solución:**
1. Verifica que `cloudflared` esté corriendo:
   ```bash
   ps aux | grep cloudflared
   ```
2. Verifica la configuración DNS en Cloudflare:
   - El registro CNAME debe apuntar al target de Facebook
   - El proxy debe estar **DESACTIVADO** (DNS only, nube gris)
3. Verifica que el dominio resuelva correctamente:
   ```bash
   dig terranote-wa.osm.lat
   ```

### Problema 4: El token de acceso ha expirado

**Causa:** Los tokens de prueba de Facebook expiran después de cierto tiempo.

**Solución:**
1. Ve a [Meta Business Suite](https://business.facebook.com/)
2. Navega a **WhatsApp** → Tu número → **API Setup**
3. Genera un nuevo **Access Token**
4. Actualiza `WHATSAPP_ACCESS_TOKEN` en el `.env`
5. Reinicia el servicio:
   ```bash
   sudo systemctl restart terranote-adapter-whatsapp
   ```

## 🧪 Probar el Webhook Manualmente

Puedes probar el webhook localmente con este comando:

```bash
curl -X POST http://localhost:3001/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "object": "whatsapp_business_account",
    "entry": [{
      "id": "test",
      "changes": [{
        "field": "messages",
        "value": {
          "messaging_product": "whatsapp",
          "metadata": {},
          "messages": [{
            "from": "573000000000",
            "id": "test123",
            "timestamp": "1734567890",
            "type": "text",
            "text": {"body": "Hola"}
          }]
        }
      }]
    }]
  }'
```

Deberías ver logs como:
- `webhook_received`
- `processing_message`
- `welcome_message_sent` (si es un usuario nuevo)

## 📋 Checklist de Verificación

- [ ] Servicio corriendo (`curl http://localhost:3001/health`)
- [ ] Webhook accesible desde internet (`curl https://terranote-wa.osm.lat/health`)
- [ ] Webhook verificado en Facebook (✅ verde)
- [ ] Suscrito al campo `messages` en Facebook
- [ ] `WHATSAPP_ACCESS_TOKEN` válido y no expirado
- [ ] `WHATSAPP_PHONE_NUMBER_ID` correcto
- [ ] Logs muestran `webhook_received` cuando envías un mensaje
- [ ] Cloudflare DNS configurado correctamente (proxy desactivado)

## 🔗 Referencias

- [Guía de configuración del webhook](./webhook-setup-guide.md)
- [Guía de configuración de DNS en Cloudflare](./cloudflare-dns-setup.md)
- [Documentación oficial de WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

