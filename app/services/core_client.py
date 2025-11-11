from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.models.interaction import InteractionRequest


class TerranoteCoreClient:
    """Cliente HTTP para interactuar con el módulo central."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.terranote_core_base_url,
            timeout=settings.terranote_core_timeout_seconds,
        )

    async def send_interaction(self, interaction: InteractionRequest) -> dict[str, Any]:
        response = await self._client.post("/api/v1/interactions", json=interaction.model_dump(mode="json"))
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()


async def send_interaction(interaction: InteractionRequest, settings: Settings) -> dict[str, Any]:
    client = TerranoteCoreClient(settings=settings)
    try:
        return await client.send_interaction(interaction)
    finally:
        await client.close()


