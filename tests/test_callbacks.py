from datetime import datetime, timezone

import json

import respx
from fastapi.testclient import TestClient
from httpx import Response

from terranote_adapter_whatsapp.main import create_app
from terranote_adapter_whatsapp.settings import Settings, get_settings


def _notification_payload() -> dict:
    return {
        "channel": "whatsapp",
        "user_id": "573000000000",
        "note_url": "https://www.openstreetmap.org/note/123456",
        "note_id": "123456",
        "latitude": 4.61,
        "longitude": -74.08,
        "text": "Hay una vía cerrada por obras.",
        "created_at": datetime(2025, 11, 11, 12, 0, tzinfo=timezone.utc).isoformat(),
    }


@respx.mock
def test_callback_sends_message_to_whatsapp(settings: Settings) -> None:
    settings = settings.model_copy(update={"notifier_secret_token": "secret"})
    assert settings.notifier_secret_token == "secret"
    get_settings.cache_clear()
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    phone_id = settings.whatsapp_phone_number_id
    base_url = str(settings.whatsapp_api_base_url)
    route = respx.post(
        f"{base_url}/{phone_id}/messages",
    ).mock(return_value=Response(200, json={"messages": [{"id": "wamid"}]}))

    response = client.post(
        "/callbacks/note-created",
        headers={"X-Terranote-Signature": "secret"},
        json=_notification_payload(),
    )

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    assert route.called
    payload = json.loads(route.calls[0].request.content)
    assert payload["to"] == "573000000000"
    assert payload["type"] == "text"
    assert "Nota creada" in payload["text"]["body"]


def test_callback_requires_signature(settings: Settings) -> None:
    settings = settings.model_copy(update={"notifier_secret_token": "secret"})
    get_settings.cache_clear()
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    response = client.post("/callbacks/note-created", json=_notification_payload())

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid signature"}


@respx.mock
def test_callback_returns_502_on_whatsapp_failure(settings: Settings) -> None:
    settings = settings.model_copy(update={"notifier_secret_token": None})
    get_settings.cache_clear()
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    base_url = str(settings.whatsapp_api_base_url)
    phone_id = settings.whatsapp_phone_number_id
    respx.post(f"{base_url}/{phone_id}/messages").mock(
        return_value=Response(500, json={"error": {"message": "fail"}})
    )

    response = client.post("/callbacks/note-created", json=_notification_payload())

    assert response.status_code == 502
    assert response.json() == {"detail": "whatsapp_error"}


