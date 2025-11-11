from __future__ import annotations

import logging
from typing import Any, Dict

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class WhatsAppCloudClient:
    """Cliente mínimo para interactuar con WhatsApp Cloud API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url="https://graph.facebook.com/v20.0",
            timeout=5.0,
            headers={
                "Authorization": f"Bearer {settings.whatsapp_token}",
                "Content-Type": "application/json",
            },
        )

    async def send_text_message(self, phone_number_id: str, to: str, text: str) -> Dict[str, Any]:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }
        logger.debug("Sending WhatsApp message: %s", payload)
        response = await self._client.post(f"/{phone_number_id}/messages", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()


