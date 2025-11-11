from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class InteractionPayloadText(BaseModel):
    type: Literal["text"] = "text"
    text: str


class InteractionPayloadLocation(BaseModel):
    type: Literal["location"] = "location"
    latitude: float
    longitude: float
    accuracy: float | None = None


InteractionPayload = InteractionPayloadText | InteractionPayloadLocation


class InteractionRequest(BaseModel):
    """Schema expected by Terranote core `POST /api/v1/interactions`."""

    channel: Literal["whatsapp"]
    user_id: str = Field(min_length=1)
    sent_at: datetime
    payload: InteractionPayload
