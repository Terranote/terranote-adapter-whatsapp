from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field


class Channel(str, Enum):
    WHATSAPP = "whatsapp"


class TextPayload(BaseModel):
    type: Literal["text"] = "text"
    text: str


class LocationPayload(BaseModel):
    type: Literal["location"] = "location"
    latitude: float
    longitude: float


class InteractionRequest(BaseModel):
    channel: Channel = Field(default=Channel.WHATSAPP)
    user_id: str
    sent_at: datetime
    payload: Union[TextPayload, LocationPayload]


