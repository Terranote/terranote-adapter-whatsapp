# Guía de integración con Terranote Core

Este adaptador consume la API pública de `terranote-core` (fase 1) para agrupar interacciones y recibir notificaciones de notas creadas. Para entender la arquitectura completa y cómo se relacionan los demás repositorios, consulta la estrategia documental en `https://github.com/Terranote/terranote-docs`.

## Endpoints utilizados

| Servicio | Método | Ruta | Descripción |
| --- | --- | --- | --- |
| Adaptador → Núcleo | `POST` | `/api/v1/interactions` | Envía interacciones normalizadas por usuario (`text` / `location`). |
| Adaptador → Núcleo | `GET` | `/api/v1/channels/{channel}/help` | Obtiene información de ayuda para un canal específico (con parámetro `lang`). |
| Núcleo → Adaptador | `POST` | `/callbacks/note-created` | Notifica que la nota fue creada y entrega la URL. |
| Adaptador (Meta) | `GET` | `/webhook` | Handshake de verificación para Meta. |
| Adaptador (Meta) | `POST` | `/webhook` | Recepción de eventos entrantes. |
| Adaptador | `GET` | `/health` | Health check sencillo. |

El contrato del núcleo está detallado en `terranote-core/docs/interfaces.md`.

> ⚠️ **IMPORTANTE:** El adaptador requiere que el core implemente el endpoint `GET /api/v1/channels/{channel}/help`. Ver [`docs/core-help-endpoint.md`](./core-help-endpoint.md) para la especificación completa y [`docs/TODO-CORE-HELP-ENDPOINT.md`](./TODO-CORE-HELP-ENDPOINT.md) para el TODO.

### Endpoint de Ayuda (`GET /api/v1/channels/{channel}/help`)

Cuando un usuario envía `/ayuda` o `/help`, el adaptador consulta este endpoint para obtener la información de ayuda dinámica.

**Parámetros:**
- `channel`: Canal del adaptador (ej: `"whatsapp"`)
- `lang`: Idioma solicitado (ej: `"es"`, `"en"`) - query parameter

**Respuesta esperada:**
```json
{
  "body": "📝 *Terranote - Comandos disponibles:*\n\n...",
  "quick_replies": [
    {"id": "cmd_crear", "title": "Crear nota"},
    {"id": "cmd_info", "title": "Más info"}
  ]
}
```

**Notas:**
- `body`: Texto del mensaje de ayuda (puede incluir Markdown de WhatsApp)
- `quick_replies`: Array opcional de botones de respuesta rápida (máximo 3)
- Si el endpoint no está disponible o falla, el adaptador usa un mensaje de ayuda local como fallback

## Requisitos del adaptador

- `channel` fijo en `"whatsapp"`.
- `user_id` corresponde al número MSISDN que provee Meta (ej. `"573000000000"`).
- `sent_at` siempre en UTC y normalizado (`datetime` con `tzinfo`).
- Payload `text` u `location` según el mensaje recibido.

## Manejo de respuestas

- `202 Accepted`: el núcleo necesita más datos (ej. falta ubicación). El adaptador puede opcionalmente notificar al usuario cuando exista un mensaje de espera.
- `note_created`: el núcleo enviará un callback con `note_url`, `latitude`, `longitude` y el texto final construido.
- `discarded`: una sesión expiró o se detectó un error. En fases futuras se podrá responder al usuario con una explicación.

## Recomendaciones de despliegue conjunto

1. Define un archivo `docker-compose` con:
   - `terranote-core`
   - `terranote-adapter-whatsapp`
   - Redis (opcional) si se usa en fases posteriores
2. Usa variables `.env` separadas para el núcleo y el adaptador.
3. Considera exponer ambos servicios detrás de un reverse proxy (NGINX, Traefik) con TLS.
4. Configura métricas y logs en un stack (ej. Loki + Promtail) para correlacionar trazas entre repositorios.

### Entorno Docker Compose compartido

El repositorio [`terranote-infra`](https://github.com/Terranote/terranote-infra) incluye un escenario E2E (`compose/whatsapp-e2e/docker-compose.yml`) que levanta:

| Servicio         | URL local             | Propósito                                      |
| ---------------- | --------------------- | ---------------------------------------------- |
| `terranote-core` | `http://localhost:8000` | API principal consumida por el adaptador.      |
| `adapter`        | `http://localhost:8001` | Webhook para Meta y callbacks de notas.        |
| `fake-osm`       | `http://localhost:8080` | API de OSM simulada para pruebas controladas.  |

Pasos resumidos:

1. Copiar `compose/whatsapp-e2e/env.whatsapp.example` a `compose/whatsapp-e2e/env.whatsapp` y completar los tokens reales.
2. Ejecutar `docker compose -f compose/whatsapp-e2e/docker-compose.yml --env-file compose/whatsapp-e2e/env.whatsapp up --build`.
3. Abrir un túnel hacia `http://localhost:8001` y registrar la URL pública en la consola de WhatsApp Cloud API.

Con esto el adaptador queda listo para procesar mensajes reales en conjunto con el núcleo.

## Pruebas de integración sugeridas

1. Levanta `terranote-core` con el fake de OSM (`docker/compose.prometheus.yml`).
2. Ejecuta el adaptador con `uvicorn` apuntando al núcleo local (`CORE_API_BASE_URL=http://localhost:8000`).
3. Simula mensajes usando la CLI de Meta:

```bash
curl -X POST "https://graph.facebook.com/v19.0/<phone-number-id>/messages" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "messaging_product": "whatsapp",
        "to": "573000000000",
        "type": "text",
        "text": {"body": "Prueba Terranote"}
      }'
```

4. Inyecta la ubicación manualmente llamando al endpoint del adaptador:

```bash
curl -X POST "http://localhost:8001/webhook" \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/location_payload.json
```

5. Comprueba que el núcleo cree la nota (usa el fake para validar) y que el callback llegue al adaptador.

Con esta guía se cubren los pasos mínimos para enlazar ambos repositorios en la fase 1.


