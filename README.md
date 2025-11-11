# terranote-adapter-whatsapp

Adaptador fase 1 para WhatsApp Cloud API que conecta con `terranote-core`. Expone un webhook compatible con los mensajes entrantes de Meta y reenvía interacciones normalizadas al módulo central; adicionalmente entrega al usuario el resultado de la creación de notas vía callback.

## Características

- Recepción de mensajes de WhatsApp (texto y ubicación) mediante Cloud API.
- Normalización de payloads hacia `POST /api/v1/interactions` del núcleo.
- Callback de creación de nota con firma opcional y envío de mensaje al usuario.
- Health check (`/health`) y endpoints de verificación de webhook (`GET /webhook`).
- Pruebas unitarias con `pytest` y `respx`.

## Requisitos previos

- Python 3.13+
- [virtualenv](https://virtualenv.pypa.io/) o equivalente
- Acceso a [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) con número registrado
- Instancia de `terranote-core` expuesta (local o remota)

## Instalación y ejecución

```bash
python3 -m virtualenv .venv
. .venv/bin/activate
pip install -e .[dev]
uvicorn terranote_adapter_whatsapp.main:app --reload
```

### Variables de entorno (`env.example`)

| Variable | Descripción |
| --- | --- |
| `APP_ENV` | Entorno de ejecución (`development`, `production`). |
| `CORE_API_BASE_URL` | URL base del módulo central. |
| `CORE_API_TIMEOUT_SECONDS` | Timeout en segundos para llamadas al núcleo. |
| `CORE_API_TOKEN` | Token opcional para autenticación contra el núcleo. |
| `WHATSAPP_VERIFY_TOKEN` | Token compartido para verificar el webhook de Meta. |
| `WHATSAPP_ACCESS_TOKEN` | Token de acceso para WhatsApp Cloud API. |
| `WHATSAPP_PHONE_NUMBER_ID` | Identificador del número asociado al bot. |
| `WHATSAPP_API_BASE_URL` | URL base de la Cloud API (por defecto `https://graph.facebook.com/v19.0`). |
| `NOTIFIER_SECRET_TOKEN` | Secreto opcional para validar callbacks desde el core. |

> Crea un archivo `.env` a partir de `env.example` y ajusta los valores antes de iniciar el adaptador.

## Endpoints expuestos

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET` | `/health` | Verificación rápida de disponibilidad. |
| `GET` | `/webhook` | Handshake de verificación (`hub.challenge`) requerido por Meta. |
| `POST` | `/webhook` | Recepción de eventos entrantes (mensajes de WhatsApp). |
| `POST` | `/callbacks/note-created` | Callback del núcleo para notificar la creación de notas. |

## Flujo de integración

1. Configura `terranote-core` (fase 1) y obtén la URL pública del adaptador.
2. Registra el webhook de WhatsApp Cloud API apuntando a `https://<tu-dominio>/webhook` con el `WHATSAPP_VERIFY_TOKEN`.
3. Al recibir mensajes, el adaptador los normaliza y llama al núcleo en `POST /api/v1/interactions`.
4. Cuando el núcleo confirma la nota, envía una solicitud `POST /callbacks/note-created`; el adaptador formatea la respuesta y notifica al usuario en WhatsApp.
5. Para ejecutar en local con túnel, usa herramientas como `ngrok` o `cloudflared`.

Consulta `docs/whatsapp-business-setup.md` para el paso a paso de configuración en Meta Business Manager.

## Pruebas y calidad

```bash
. .venv/bin/activate
pytest
```

Para ejecutar con cobertura:

```bash
pytest --cov --cov-report=term-missing
```

Se recomienda añadir `ruff`, `mypy` y `pytest` como jobs en CI (ver TODO `todo-ci`).

## Estructura

- `src/terranote_adapter_whatsapp/main.py`: instancia de FastAPI.
- `src/terranote_adapter_whatsapp/routes`: endpoints (`/webhook`, `/callbacks`, `/health`).
- `src/terranote_adapter_whatsapp/services`: normalización de mensajes.
- `src/terranote_adapter_whatsapp/clients`: clientes HTTP hacia el núcleo y WhatsApp.
- `src/terranote_adapter_whatsapp/schemas`: modelos Pydantic.
- `tests`: pruebas unitarias con `pytest`.
- `docs/whatsapp-business-setup.md`: guía para registrar el bot en Cloud API.

## Desarrollo local

- Ejecuta `pytest` tras cada cambio relevante.
- Usa `uvicorn ... --reload` para pruebas manuales.
- Registra logs mediante `structlog`; configura `LOGLEVEL` para ajustar verbosidad.

## Recursos adicionales

- [Documentación oficial de WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Repositorio `terranote-core`](https://github.com/angoca/terranote-core) para la contraparte central.

## Pruebas end-to-end rápidas

Consulta el repositorio [`terranote-infra`](https://github.com/Terranote/terranote-infra) para levantar el stack completo (`terranote-core`, adaptador y fake-OSM) mediante Docker Compose. Allí encontrarás:

- Plantillas de variables (`env.whatsapp.example`).
- `docker-compose.yml` listo para exponer el adaptador en `http://localhost:8001`.
- Instrucciones para abrir un túnel (`ngrok`/`cloudflared`) y registrar el webhook en Meta.

Una vez desplegado, sigue la guía de WhatsApp Business ubicada en `docs/whatsapp-business-setup.md` para enviar mensajes de prueba y validar la creación de notas.

## Licencia

GPL-3.0-or-later, ver `LICENSE`.

