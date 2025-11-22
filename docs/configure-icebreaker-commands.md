# Configurar Icebreaker y Commands en WhatsApp Business API

Esta guía explica cómo configurar los **Icebreakers** (mensajes de bienvenida con botones) y los **Commands** (comandos rápidos) en WhatsApp Business API para mejorar la experiencia del usuario.

## ¿Qué son Icebreakers y Commands?

- **Icebreakers**: Botones de inicio rápido que aparecen cuando un usuario inicia una conversación por primera vez o después de 24 horas sin interacción. Ayudan a guiar al usuario desde el inicio.
- **Commands**: Palabras clave o frases que los usuarios pueden enviar para activar respuestas automáticas o flujos específicos.

## Paso 1: Implementar Mensaje de Bienvenida (Icebreaker)

**⚠️ Importante:** En WhatsApp Business API (Cloud API), **NO existe una opción de "Welcome Message" en Meta Business Manager** como en la app móvil de WhatsApp Business. 

En su lugar, debes **implementar la lógica en tu adaptador** para detectar cuando un usuario inicia una conversación y enviar automáticamente un mensaje de bienvenida con botones interactivos.

### Solución: Implementar en el Adaptador

La mejor forma es detectar el primer mensaje de un usuario y responder con un mensaje de bienvenida que incluya botones interactivos (Quick Replies o Interactive Buttons).

### Opción A: Usar Quick Replies (Botones de Respuesta Rápida)

**Implementación práctica:**

1. **Agregar método para enviar mensaje con botones** en `WhatsAppClient`:

```python
# En src/terranote_adapter_whatsapp/clients/whatsapp.py
async def send_welcome_message(self, to: str) -> httpx.Response:
    """Send welcome message with quick reply buttons."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": "¡Hola! 👋 Bienvenido a Terranote.\n\nPuedes crear notas enviándome un mensaje de texto y luego tu ubicación.\n\n¿Cómo puedo ayudarte?"
        },
        "quick_replies": [
            {
                "type": "reply",
                "reply": {
                    "id": "cmd_crear",
                    "title": "Crear nota"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "cmd_ayuda",
                    "title": "Ver ayuda"
                }
            },
            {
                "type": "reply",
                "reply": {
                    "id": "cmd_info",
                    "title": "Más info"
                }
            }
        ]
    }
    
    async with httpx.AsyncClient(base_url=str(self._base_url), headers=self._headers) as client:
        endpoint = f"/{self._phone_number_id}/messages"
        return await client.post(endpoint, json=payload)
```

2. **Detectar primer mensaje y enviar bienvenida** en el webhook:

```python
# En src/terranote_adapter_whatsapp/routes/webhook.py
# Agregar al inicio del archivo (necesitarás una forma de trackear usuarios nuevos)
# Opción simple: usar un set en memoria (para producción, usa Redis o base de datos)

_seen_users: set[str] = set()  # En producción, usa Redis o DB

# Dentro de receive_webhook, antes de procesar el mensaje:
user_id = message.from_

# Verificar si es un usuario nuevo
if user_id not in _seen_users:
    _seen_users.add(user_id)
    # Enviar mensaje de bienvenida
    whatsapp_client = WhatsAppClient(settings)
    try:
        await whatsapp_client.send_welcome_message(user_id)
        logger.info("welcome_message_sent", user_id=user_id)
    except Exception as exc:
        logger.error("failed_to_send_welcome", user_id=user_id, error=str(exc))
    # Continuar procesando el mensaje normalmente
```

**Nota:** Esta implementación básica usa un set en memoria. Para producción, considera usar Redis o una base de datos para trackear usuarios de forma persistente.

## Paso 2: Configurar Commands (Comandos Rápidos)

Los Commands pueden implementarse de dos formas:

### Opción A: Implementar en el Adaptador (Recomendado)

Puedes agregar lógica en el adaptador para reconocer comandos específicos y responder automáticamente.

**Ejemplo de implementación:**

1. **Modificar el procesador de mensajes** para detectar comandos:

```python
# En src/terranote_adapter_whatsapp/services/message_processor.py
def is_command(self, text: str) -> bool:
    """Check if message is a command (starts with /)"""
    return text.strip().startswith("/")

def process_command(self, user_id: str, command: str) -> str | None:
    """Process command and return response, or None if should forward to core"""
    command = command.strip().lower()
    
    if command == "/ayuda" or command == "/help":
        return "📝 *Terranote - Comandos disponibles:*\n\n" \
               "• /crear - Crear una nueva nota\n" \
               "• /listar - Ver mis notas\n" \
               "• /ayuda - Mostrar esta ayuda"
    
    if command == "/listar":
        # Aquí podrías hacer una llamada al core para obtener las notas del usuario
        return "🔍 Consultando tus notas..."
    
    # Si no es un comando reconocido, retornar None para procesarlo normalmente
    return None
```

2. **Modificar el webhook** para procesar comandos antes de enviar al core:

```python
# En src/terranote_adapter_whatsapp/routes/webhook.py
from ..clients.whatsapp import WhatsAppClient

# Dentro de receive_webhook, antes de enviar al core:
if message.type == "text" and message.text:
    text = message.text.body
    
    # Verificar si es un comando
    if processor.is_command(text):
        response = processor.process_command(message.from_, text)
        if response:
            # Enviar respuesta directa sin pasar por el core
            whatsapp_client = WhatsAppClient(settings)
            await whatsapp_client.send_text_message(message.from_, response)
            processed += 1
            continue  # No enviar al core
```

### Opción B: Usar Quick Replies de WhatsApp

Los Quick Replies son botones que aparecen después de enviar un mensaje, permitiendo al usuario responder rápidamente.

**Ejemplo de mensaje con Quick Replies:**

```python
# En src/terranote_adapter_whatsapp/clients/whatsapp.py
async def send_text_message_with_quick_replies(
    self, to: str, body: str, quick_replies: list[dict]
) -> httpx.Response:
    """Send a text message with quick reply buttons."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
        "quick_replies": quick_replies
    }
    
    async with httpx.AsyncClient(base_url=str(self._base_url), headers=self._headers) as client:
        endpoint = f"/{self._phone_number_id}/messages"
        return await client.post(endpoint, json=payload)

# Ejemplo de uso:
quick_replies = [
    {
        "type": "reply",
        "reply": {
            "id": "cmd_crear",
            "title": "Crear nota"
        }
    },
    {
        "type": "reply",
        "reply": {
            "id": "cmd_ayuda",
            "title": "Ayuda"
        }
    }
]
```

## Paso 3: Probar la Configuración

1. **Probar Icebreakers:**
   - Inicia una nueva conversación desde WhatsApp (o espera 24 horas)
   - Deberías ver los botones de inicio rápido
   - Haz clic en cada botón y verifica que se envíe la respuesta correcta

2. **Probar Commands:**
   - Envía un comando desde WhatsApp (ej: `/ayuda`)
   - Verifica que el adaptador responda correctamente
   - Revisa los logs del servidor para confirmar el procesamiento

## Comandos Sugeridos para Terranote

Basándote en la funcionalidad de Terranote, estos son comandos útiles:

| Comando | Descripción | Acción |
|---------|-------------|--------|
| `/ayuda` o `/help` | Mostrar ayuda | Lista de comandos disponibles |
| `/crear` | Crear nueva nota | Inicia flujo de creación de nota |
| `/listar` | Ver mis notas | Muestra notas del usuario |
| `/ubicacion` | Enviar ubicación | Solicita ubicación al usuario |

## Consideraciones Importantes

1. **Límites de Meta:**
   - Los Icebreakers solo aparecen en la primera interacción o después de 24 horas sin comunicación
   - Máximo 4 botones en Icebreakers
   - Los Quick Replies tienen límite de 3 botones por mensaje

2. **Ventana de 24 horas:**
   - Meta permite enviar mensajes sin restricciones dentro de las primeras 24 horas después del último mensaje del usuario
   - Después de 24 horas, solo puedes responder a mensajes del usuario o usar plantillas aprobadas

3. **Plantillas de mensajes:**
   - Para mensajes fuera de la ventana de 24 horas, necesitas usar plantillas aprobadas por Meta
   - Las plantillas deben ser aprobadas antes de usarse

## Próximos Pasos

1. ✅ Implementar mensaje de bienvenida en el adaptador (detectar primer mensaje)
2. ✅ Agregar método `send_welcome_message` con Quick Replies en `WhatsAppClient`
3. ✅ Implementar procesamiento de comandos en el adaptador
4. ✅ Probar ambos flujos con mensajes reales
5. ✅ Documentar los comandos disponibles para los usuarios

## Referencias

- [Documentación oficial de WhatsApp Business API - Welcome Messages](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-welcome-message)
- [Documentación oficial de WhatsApp Business API - Interactive Messages](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages#interactive-messages)
- [Meta Business Manager](https://business.facebook.com/)

