# Guía de integración con Terranote Core

Este adaptador consume la API pública de `terranote-core` (fase 1) para agrupar interacciones y recibir notificaciones de notas creadas.

## Endpoints utilizados

| Servicio | Método | Ruta | Descripción |
| --- | --- | --- | --- |
| Adaptador → Núcleo | `POST` | `/api/v1/interactions` | Envía interacciones normalizadas por usuario (`text` / `location`). |
| Núcleo → Adaptador | `POST` | `/callbacks/note-created` | Notifica que la nota fue creada y entrega la URL. |
| Adaptador (Meta) | `GET` | `/webhook` | Handshake de verificación para Meta. |
| Adaptador (Meta) | `POST` | `/webhook` | Recepción de eventos entrantes. |
| Adaptador | `GET` | `/health` | Health check sencillo. |

El contrato del núcleo está detallado en `terranote-core/docs/interfaces.md`.

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

### Entorno Docker Compose incluido

El repositorio del adaptador provee `docker-compose.e2e.yml` para levantar el stack mínimo:

```bash
cp env.example .env  # completar valores reales
docker compose -f docker-compose.e2e.yml up --build
```

Servicios expuestos:

| Servicio | URL local | Propósito |
| --- | --- | --- |
| `terranote-core` | `http://localhost:8000` | API principal consumida por el adaptador. |
| `adapter` | `http://localhost:8001` | Webhook para Meta y callbacks de notas. |
| `fake-osm` | `http://localhost:8080` | API de OSM simulada para pruebas controladas. |

Para exponer el adaptador a Meta ejecuta un túnel (`ngrok http 8001` o `cloudflared tunnel run`) y registra la URL en la consola de WhatsApp Cloud API junto con el verify token.

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


