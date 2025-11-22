import json

import respx
from httpx import Response


def _sample_event(message: dict) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1555000000",
                                "phone_number_id": "phone-id",
                            },
                            "contacts": [],
                            "messages": [message],
                        },
                    }
                ],
            }
        ],
    }


def test_webhook_verification_accepts_valid_token(client):
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "verify-token",
        },
    )

    assert response.status_code == 200
    assert response.text == "12345"  # Facebook expects plain text, not JSON


def test_webhook_verification_rejects_invalid_token(client):
    response = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "12345",
            "hub.verify_token": "wrong",
        },
    )

    assert response.status_code == 403


@respx.mock
def test_webhook_forwards_text_message_to_core(client):
    route = respx.post("http://localhost:8000/api/v1/interactions").mock(
        return_value=Response(202, json={"status": "queued"})
    )
    payload = _sample_event(
        {
            "from": "573000000000",
            "id": "wamid.HBgLN...",
            "timestamp": "1731326400",
            "type": "text",
            "text": {"body": "Hola"},
        }
    )

    response = client.post("/webhook", json=payload)

    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "processed": 1}
    assert route.called
    sent_payload = json.loads(route.calls[0].request.content)
    assert sent_payload["channel"] == "whatsapp"
    assert sent_payload["payload"]["type"] == "text"
    assert sent_payload["payload"]["text"] == "Hola"


@respx.mock
def test_webhook_skips_unsupported_message_type(client):
    route = respx.post("http://localhost:8000/api/v1/interactions").mock(return_value=Response(202))
    payload = _sample_event(
        {
            "from": "573000000000",
            "id": "wamid.HBgLN...",
            "timestamp": "1731326400",
            "type": "image",
            "image": {"id": "ABC"},
        }
    )

    response = client.post("/webhook", json=payload)

    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "processed": 0}
    assert not route.called


@respx.mock
def test_webhook_returns_502_when_core_rejects(client):
    respx.post("http://localhost:8000/api/v1/interactions").mock(
        return_value=Response(500, json={"detail": "error"})
    )
    payload = _sample_event(
        {
            "from": "573000000000",
            "id": "wamid.HBgLN...",
            "timestamp": "1731326400",
            "type": "text",
            "text": {"body": "Hola"},
        }
    )

    response = client.post("/webhook", json=payload)

    assert response.status_code == 502
    assert response.json() == {"detail": "core_error"}
