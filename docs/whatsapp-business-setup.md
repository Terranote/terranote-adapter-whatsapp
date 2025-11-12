# Guía de configuración para WhatsApp Cloud API

Este documento describe el proceso recomendado para enlazar el adaptador con WhatsApp Cloud API durante la fase 1 de Terranote.

## 1. Preparativos en Meta Business Suite

1. Accede a [developers.facebook.com](https://developers.facebook.com/) con una cuenta que tenga permisos sobre un negocio.
2. Crea una **App** de tipo *Business* o usa una existente.
3. En la sección **WhatsApp**, agrega un número de teléfono. Para entornos de prueba, Meta ofrece un número temporal con código QR y token.
4. Registra la aplicación en modo **Sandbox** o **Production** según corresponda. Conserva:
   - `Phone Number ID`
   - `WhatsApp Business Account ID`
   - `Permanent Access Token` (genera uno de larga duración desde la consola).

## 2. Configuración del webhook

1. En la sección **Configuration → Webhooks**, agrega la URL pública del adaptador (ej. `https://bot.terranote.dev/webhook`).
2. Define el **Verify token** con un valor conocido; copia el mismo string en `WHATSAPP_VERIFY_TOKEN`.
3. Selecciona los campos a suscribirse:
   - `messages`
   - `message_reactions` (opcional)
4. Meta enviará una solicitud `GET` con `hub.challenge`. Verifica que el adaptador responda `200` y `{"hub_challenge": "<token>"}`.

> Para entornos locales usa `ngrok` (o similar) y actualiza la URL cada vez que cambie el túnel.

## 3. Variables de entorno del adaptador

Actualiza el archivo `.env` con los valores obtenidos:

```env
WHATSAPP_ACCESS_TOKEN=<permanent-token>
WHATSAPP_PHONE_NUMBER_ID=<phone-number-id>
WHATSAPP_VERIFY_TOKEN=<verify-token>
WHATSAPP_API_BASE_URL=https://graph.facebook.com/v19.0
CORE_API_BASE_URL=https://core.terranote.dev
NOTIFIER_SECRET_TOKEN=<opcional>
```

- `CORE_API_BASE_URL` apunta al servicio `terranote-core`.
- `NOTIFIER_SECRET_TOKEN` se utilizará para firmar el callback `POST /callbacks/note-created`.

## 4. Configurar el callback del núcleo

1. En la instancia de `terranote-core`, define la variable `NOTIFIER_WHATSAPP_ENDPOINT` con la URL pública del adaptador: `https://bot.terranote.dev/callbacks/note-created`.
2. Si usas firma (`NOTIFIER_SECRET_TOKEN`), configura el mismo valor en ambos servicios.
3. Verifica que el adaptador responda `202 Accepted` cuando reciba un callback de prueba.

## 5. Pruebas end-to-end

1. Envia un mensaje desde WhatsApp al número configurado (texto seguido de ubicación dentro del margen de tiempo).
2. Observa que `terranote-core` cree la nota en OSM y ejecute la notificación al adaptador.
3. Confirma que el adaptador responda al usuario con la URL de la nota.

## 6. Consideraciones adicionales

- **Seguridad:** guarda los tokens de acceso en un almacén seguro (ej. Secret Manager o Vault). Para entornos locales, evita subir `.env` a repositorios públicos.
- **Límites de Meta:** los tokens de prueba expiran; configura recordatorios para renovarlos y considera migrar a tokens permanentes en producción.
- **Logs:** habilita `LOGLEVEL=info` para tener trazas claras en despliegues productivos; `debug` solo en ambientes controlados.
- **Errores comunes:**
  - `401 Invalid OAuth access token`: verifica que `WHATSAPP_ACCESS_TOKEN` siga vigente.
  - `403 (#10) Application does not have capability`: asegura que la app tenga habilitada la capacidad de mensajería del teléfono.
  - `Failed verification`: revisa que el token de verificación coincida y que el adaptador esté accesible desde Internet.

Con esto el adaptador queda listo para operar en la fase 1. Mantén la guía actualizada si Meta modifica los pasos de la consola o API.

> Para referencias globales de arquitectura y operación, visita `https://github.com/Terranote/terranote-docs`.


