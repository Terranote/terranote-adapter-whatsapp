# Guía Paso a Paso: Configurar el Webhook de WhatsApp

Esta guía te ayudará a configurar el webhook de WhatsApp paso a paso.

## ✅ Paso 1: Verificar que tu servidor esté corriendo

Antes de configurar el webhook en Facebook, necesitas que tu servidor esté accesible desde Internet.

### Opción A: Dominio personalizado con Cloudflare DNS (Recomendado para producción)

Si Facebook te proporcionó un target CNAME (ej: `1b718247-fe2d-4391-84c0-819c1501e6c2`):

1. **Configura el CNAME en Cloudflare:**
   - Ve a Cloudflare → Tu dominio → DNS → Records
   - Agrega un registro CNAME:
     - **Type:** `CNAME`
     - **Name:** `terranote-wa` (o el que prefieras)
     - **Target:** `1b718247-fe2d-4391-84c0-819c1501e6c2` (el que te dio Facebook)
     - **Proxy status:** ❌ Desactivado (DNS only) - Importante: Facebook requiere DNS only, no Proxied
     - **TTL:** Auto
   - Guarda el registro

2. **Espera la propagación DNS** (generalmente unos minutos)

3. **Usa tu dominio en Facebook:**
   - URL del webhook: `https://terranote-wa.tu-dominio.com/webhook`

📖 **Ver guía completa:** `docs/cloudflare-dns-setup.md`

### Opción B: Desarrollo local con túnel temporal (cloudflared)

**Con cloudflared:**
```bash
# Instala cloudflared si no lo tienes
cloudflared tunnel --url http://localhost:3001
```

Copia la URL HTTPS que te da (ejemplo: `https://abc123.trycloudflare.com`)

⚠️ **Nota:** La URL temporal cambia cada vez que reinicias cloudflared.

### Opción C: Servidor de producción directo

Si ya tienes el servidor en producción (192.168.0.7), asegúrate de que:
- El servicio esté corriendo: `sudo systemctl status terranote-adapter-whatsapp`
- El puerto 3001 esté abierto y accesible desde Internet
- Si usas un dominio, que apunte correctamente

## ✅ Paso 2: Verificar el Verify Token en tu .env

Tu archivo `.env` ya tiene configurado un verify token seguro:

```env
WHATSAPP_VERIFY_TOKEN=PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8
```

**⚠️ IMPORTANTE:** Este mismo token debes usarlo en Facebook.

## ✅ Paso 3: Configurar el webhook en Facebook

1. **Ve a Facebook Developers:**
   - Accede a [https://developers.facebook.com/](https://developers.facebook.com/)
   - Selecciona tu app

2. **Navega a la configuración del webhook:**
   - En el menú lateral izquierdo, busca **"WhatsApp"**
   - Dentro de WhatsApp, haz clic en **"Configuration"** (Configuración)
   - Busca la sección **"Webhooks"**

3. **Configura el webhook:**
   - Haz clic en **"Configure webhooks"** o en el botón **"Edit"** si ya existe uno
   - Completa el formulario:
     
     **Callback URL:**
     - Si usas dominio personalizado con Cloudflare: `https://terranote-wa.tu-dominio.com/webhook`
       - Ejemplo: `https://terranote-wa.terranote.dev/webhook`
     - Si estás en desarrollo local con cloudflared: `https://tu-url-cloudflared/webhook`
       - Ejemplo: `https://abc123.trycloudflare.com/webhook`
     - Si estás en producción directa: `https://tu-dominio.com/webhook`
       - Ejemplo: `https://whatsapp.terranote.dev/webhook`
     
     **Verify token:**
     - Pega exactamente este token: `PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8`
     - ⚠️ **Debe ser EXACTAMENTE igual** al que tienes en tu `.env`

4. **Verificar el webhook:**
   - Haz clic en **"Verify and save"** (Verificar y guardar)
   - Facebook enviará una petición GET a tu servidor
   - Si todo está correcto, verás un ✅ verde que dice "Verified"

5. **Suscribirse a eventos:**
   - Una vez verificado, verás una lista de campos
   - Marca estos campos:
     - ✅ **`messages`** (obligatorio)
     - ✅ **`message_reactions`** (opcional, pero recomendado)
   - Guarda los cambios

## ✅ Paso 4: Verificar que funciona

### 4.1. Verificar el health check

```bash
curl http://localhost:3001/health
```

Debería responder: `{"status":"ok"}`

### 4.2. Verificar el endpoint del webhook

```bash
# Prueba la verificación manualmente
curl "http://localhost:3001/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8"
```

Debería responder: `{"hub_challenge":"test123"}`

### 4.3. Enviar un mensaje de prueba

1. Desde WhatsApp, envía un mensaje al número de prueba que configuraste
2. Revisa los logs de tu servidor:
   ```bash
   # Si estás en desarrollo
   # Verás los logs en la terminal donde corre uvicorn
   
   # Si estás en producción
   sudo journalctl -u terranote-adapter-whatsapp -f
   ```
3. Deberías ver logs indicando que se recibió el mensaje

## 🔧 Solución de problemas

### Error: "Verification failed" en Facebook

**Causas posibles:**
1. El verify token no coincide exactamente
   - Verifica que sea el mismo en `.env` y en Facebook
   - No debe tener espacios extra al inicio o final
2. El servidor no está accesible desde Internet
   - Verifica que ngrok/cloudflared esté corriendo
   - Verifica que el puerto esté abierto
3. El endpoint `/webhook` no responde correctamente
   - Verifica que el servidor esté corriendo
   - Prueba el health check primero

**Solución:**
```bash
# Verifica que el servidor esté corriendo
curl http://localhost:3001/health

# Verifica el verify token en .env
grep WHATSAPP_VERIFY_TOKEN .env

# Asegúrate de que sea exactamente el mismo en Facebook
```

### El webhook está verificado pero no recibe mensajes

**Causas posibles:**
1. No estás suscrito al campo `messages`
2. El número de teléfono no está activo
3. Hay un error en el procesamiento de mensajes

**Solución:**
1. Verifica en Facebook que `messages` esté marcado
2. Revisa los logs del servidor para ver errores
3. Prueba enviando un mensaje simple de texto

### Error 403 en la verificación

Si ves un error 403, verifica:
1. Que el `hub.mode` sea `subscribe`
2. Que el `hub.verify_token` coincida exactamente
3. Revisa los logs del servidor para más detalles

## 📝 Resumen de valores

| Valor | Dónde está | Ejemplo |
|-------|------------|---------|
| **Callback URL** | Lo defines tú | `https://abc123.ngrok.io/webhook` |
| **Verify Token** | En tu `.env` | `PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8` |
| **Campos a suscribir** | En Facebook | `messages`, `message_reactions` |

## ✅ Checklist final

- [ ] Servidor corriendo y accesible desde Internet
- [ ] Verify token configurado en `.env`
- [ ] Webhook configurado en Facebook con la misma URL y token
- [ ] Webhook verificado (✅ verde en Facebook)
- [ ] Suscrito al campo `messages`
- [ ] Health check responde correctamente
- [ ] Mensaje de prueba enviado y recibido

¡Listo! Tu webhook debería estar funcionando correctamente.

