# Guía Rápida: Configuración Inicial con Facebook

Esta guía te ayudará a configurar el adaptador de WhatsApp desde cero ahora que tienes acceso a Facebook.

## Paso 1: Crear la App en Facebook Developers

1. **Accede a Facebook Developers:**
   - Ve a [https://developers.facebook.com/](https://developers.facebook.com/)
   - Inicia sesión con tu cuenta de Facebook

2. **Crear una nueva App:**
   - Haz clic en "Mis Apps" → "Crear App"
   - Selecciona el tipo de app: **"Business"** o **"Otro"**
   - Completa el formulario:
     - Nombre de la app: `Terranote WhatsApp Adapter` (o el que prefieras)
     - Email de contacto: tu email
     - Propósito de la app: selecciona "WhatsApp" o "Business"
   - Haz clic en "Crear App"

3. **Agregar WhatsApp al producto:**
   - En el panel de tu app, busca la sección "Agregar productos a tu app"
   - Haz clic en "WhatsApp" → "Configurar"
   - Esto te llevará a la configuración de WhatsApp

## Paso 2: Configurar WhatsApp Business API

Una vez que agregaste WhatsApp a tu app, verás la sección "Send and receive messages" con dos partes principales:

### 2.1. Obtener el Access Token

1. En la parte superior verás la sección **"Access Token"**
2. Haz clic en **"Generate access token"** (Generar token de acceso)
3. Selecciona tu cuenta de WhatsApp Business
4. **Copia el token completo** que aparece en el campo (es muy largo)
   - Este es tu `WHATSAPP_ACCESS_TOKEN`
   - ⚠️ **Importante:** Los tokens de prueba expiran. Para producción, necesitarás un token permanente.

### 2.2. Obtener el Phone Number ID

1. En la sección **"Send and receive messages"** → **"Step 1: Select phone numbers"**
2. Selecciona un número de prueba (aparece como "Test number: +1 555 XXX XXXX")
3. Debajo verás dos IDs importantes:
   - **Phone number ID:** Un número largo (ej: `864235020113006`)
     - Este es tu `WHATSAPP_PHONE_NUMBER_ID` ⬅️ **Lo necesitas para `.env`**
   - **WhatsApp Business Account ID:** Otro número largo
     - Este es opcional, pero anótalo por si lo necesitas más adelante

### Resumen de valores a copiar:

| Valor en Facebook | Variable en .env | Dónde encontrarlo |
|-------------------|------------------|-------------------|
| Access Token (campo largo) | `WHATSAPP_ACCESS_TOKEN` | Sección "Access Token" → botón "Copy" |
| Phone number ID | `WHATSAPP_PHONE_NUMBER_ID` | "Step 1" → debajo del número seleccionado |
| WhatsApp Business Account ID | (opcional) | "Step 1" → debajo del número seleccionado |

## Paso 3: Configurar el Webhook

### 3.1. Preparar el servidor local (para desarrollo)

Para desarrollo local, necesitas exponer tu servidor a Internet. Usa una de estas opciones:

**Opción A: cloudflared (recomendado)**
```bash
# Instala cloudflared si no lo tienes: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
cloudflared tunnel --url http://localhost:3001

# Copia la URL HTTPS que te da (ej: https://abc123.trycloudflare.com)
```

**Opción B: ngrok (alternativa)**
```bash
# Instala ngrok si no lo tienes: https://ngrok.com/download
ngrok http 3001

# Copia la URL HTTPS que te da (ej: https://abc123.ngrok.io)
```

### 3.2. Configurar el webhook en Facebook

1. En la sección de WhatsApp de tu app, busca el menú lateral y ve a **"Configuration"** (Configuración)
2. En la sección **"Webhooks"**, haz clic en **"Configure webhooks"** o **"Edit"**
3. Completa el formulario:
   - **Callback URL:** `https://tu-dominio.com/webhook` 
     - Para desarrollo local: usa la URL de cloudflared + `/webhook`
     - Ejemplo: `https://abc123.trycloudflare.com/webhook`
   - **Verify token:** Usa este token que ya está configurado en tu `.env`:
     - Token: `PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8`
     - ⚠️ **IMPORTANTE:** Debe ser EXACTAMENTE el mismo que en tu `.env`
4. Haz clic en **"Verify and save"** (Verificar y guardar)
   - Facebook enviará una petición GET a tu webhook para verificar
   - Si tu servidor está corriendo y configurado correctamente, debería responder con éxito
5. Una vez verificado, suscríbete a los campos:
   - ✅ Marca `messages` (obligatorio)
   - ✅ Marca `message_reactions` (opcional)
   - Guarda los cambios

## Paso 4: Configurar el archivo .env

Edita el archivo `.env` en la raíz del proyecto con los valores obtenidos de Facebook:

```env
APP_ENV=development
CORE_API_BASE_URL=https://terranote-core.local  # Ajusta según tu configuración
CORE_API_TIMEOUT_SECONDS=5.0
CORE_API_TOKEN=  # Opcional, si tu core requiere autenticación

# ⬇️ VALORES DE FACEBOOK - Copia exactamente como aparecen ⬇️

# 1. Access Token (de la sección "Access Token", botón "Copy")
WHATSAPP_ACCESS_TOKEN=EAAIn2n3thJsBQODG4PuE83hbPzJZC4KMAEQYLhDOepEtwZAvnXdRX3vZCAHcutMLMpRfJuBHDZBPvRl1CjUf5yZBpRf3Izn6Jjqvlmos3El6ixy63WzjIgLCwZCvbKt3yRyoODgoavkv8xT7RYqgdZBLVZA9qe0rPx4ZAdD5DfZBzImalSAYZA9HNcIbcHvUMdgwBkdmgPj11fh7G4uS3ZAdI2NrNi0ImPxjs3AZAMRtvLnsCkergAf9zwhidZB8tmTCZAhkW6AYvSnjQRZAB1TtNGknzAZDZD

# 2. Phone Number ID (de "Step 1: Select phone numbers", debajo del número)
WHATSAPP_PHONE_NUMBER_ID=864235020113006

# 3. Verify Token (ya generado automáticamente - úsalo en Facebook)
WHATSAPP_VERIFY_TOKEN=PXfiE_5U2l7OsfJDa_M-xS7m7XxeXbYZQ3k5JBnbZT8

# 4. API Base URL (no cambies esto a menos que Facebook lo indique)
WHATSAPP_API_BASE_URL=https://graph.facebook.com/v19.0

# ⬆️ FIN DE VALORES DE FACEBOOK ⬆️

NOTIFIER_SECRET_TOKEN=  # Opcional, para firmar callbacks
```

### 📝 Notas importantes:

- **WHATSAPP_ACCESS_TOKEN:** Copia el token completo desde Facebook (es muy largo, asegúrate de copiarlo completo)
- **WHATSAPP_PHONE_NUMBER_ID:** Es el número que aparece en "Phone number ID" (ej: `864235020113006`)
- **WHATSAPP_VERIFY_TOKEN:** Lo defines tú cuando configures el webhook. Debe ser el mismo que pongas en Facebook
- **WHATSAPP_API_BASE_URL:** Generalmente no necesitas cambiarlo, pero verifica la versión de la API en Facebook

## Paso 5: Iniciar el servidor

```bash
# Activa el entorno virtual
source .venv/bin/activate

# Inicia el servidor
uvicorn terranote_adapter_whatsapp.main:app --reload --port 3001
```

## Paso 6: Verificar la conexión

1. **Verifica el health check:**
   ```bash
   curl http://localhost:3001/health
   ```
   Debería responder: `{"status":"ok"}`

2. **Verifica el webhook:**
   - Facebook debería haber verificado automáticamente el webhook cuando lo configuraste
   - Si no, puedes probarlo manualmente visitando la URL de verificación en el navegador

3. **Envía un mensaje de prueba:**
   - Desde WhatsApp, envía un mensaje al número configurado
   - Revisa los logs del servidor para ver si recibió el mensaje

## Paso 7: Configurar terranote-core (si aplica)

Si tienes `terranote-core` corriendo, configura:

1. Variable de entorno en `terranote-core`:
   ```env
   NOTIFIER_WHATSAPP_ENDPOINT=https://tu-dominio.com/callbacks/note-created
   ```

2. Si usas `NOTIFIER_SECRET_TOKEN`, configúralo igual en ambos servicios

## Solución de problemas comunes

### Error: "401 Invalid OAuth access token"
- El token ha expirado o es incorrecto
- Genera un nuevo token en Facebook Developers

### Error: "403 Application does not have capability"
- Asegúrate de que la app tenga habilitada la capacidad de mensajería
- Verifica que el número de teléfono esté correctamente configurado

### Error: "Failed verification" en el webhook
- Verifica que `WHATSAPP_VERIFY_TOKEN` coincida exactamente
- Asegúrate de que tu servidor sea accesible desde Internet
- Revisa que el endpoint `/webhook` esté respondiendo correctamente

### El webhook no recibe mensajes
- Verifica que estés suscrito al campo `messages` en la configuración del webhook
- Asegúrate de que el número de teléfono esté en modo activo (no solo Sandbox si estás en producción)
- Revisa los logs del servidor para ver errores

## Próximos pasos

- Revisa `docs/whatsapp-business-setup.md` para más detalles
- Consulta `docs/integration-guide.md` para entender el flujo completo
- Para producción, considera migrar a tokens permanentes y configurar SSL adecuadamente

