import httpx

from ..settings import Settings


class WhatsAppClient:
    """Client to interact with WhatsApp Cloud API."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.whatsapp_api_base_url
        self._phone_number_id = settings.whatsapp_phone_number_id
        self._headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, to: str, body: str) -> httpx.Response:
        """Send a text message to a WhatsApp user."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }

        async with httpx.AsyncClient(base_url=str(self._base_url), headers=self._headers) as client:
            endpoint = f"/{self._phone_number_id}/messages"
            return await client.post(endpoint, json=payload)

    async def send_text_message_with_quick_replies(
        self, to: str, body: str, quick_replies: list[dict]
    ) -> httpx.Response:
        """Send a text message with quick reply buttons."""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }

        # Add quick replies if provided
        if quick_replies:
            payload["quick_replies"] = [
                {
                    "type": "reply",
                    "reply": {
                        "id": reply["id"],
                        "title": reply["title"],
                    },
                }
                for reply in quick_replies
            ]

        async with httpx.AsyncClient(base_url=str(self._base_url), headers=self._headers) as client:
            endpoint = f"/{self._phone_number_id}/messages"
            return await client.post(endpoint, json=payload)
