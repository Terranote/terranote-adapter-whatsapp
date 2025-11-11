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
    assert response.json() == {"hub_challenge": "12345"}


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

