from collections.abc import Mapping

import httpx

from ..schemas.interactions import InteractionRequest
from ..settings import Settings


class TerranoteCoreClient:
    """HTTP client to interact with Terranote core API."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.core_api_base_url
        self._timeout = settings.core_api_timeout_seconds
        self._headers: Mapping[str, str] = (
            {"Authorization": f"Bearer {settings.core_api_token}"}
            if settings.core_api_token
            else {}
        )

    async def send_interaction(self, interaction: InteractionRequest) -> httpx.Response:
        """Forward a normalized interaction to Terranote core."""
        async with httpx.AsyncClient(
            base_url=str(self._base_url),
            timeout=self._timeout,
            headers=self._headers,
        ) as client:
            return await client.post(
                "/api/v1/interactions",
                json=interaction.model_dump(mode="json"),
            )
