from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, ConfigDict


class MessageText(BaseModel):
    """Text message payload from WhatsApp Cloud API."""

    body: str


class MessageLocation(BaseModel):
    """Location message payload from WhatsApp Cloud API."""

    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None


class Message(BaseModel):
    """Representation of a WhatsApp message."""

    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from")
    id: str
    timestamp: datetime
    type: Literal["text", "location"]
    text: MessageText | None = None
    location: MessageLocation | None = None


class ChangeValue(BaseModel):
    """Inner change payload defined by Meta."""

    messaging_product: Literal["whatsapp"]
    metadata: dict[str, Any]
    contacts: list[dict[str, Any]] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)


class Change(BaseModel):
    field: str
    value: ChangeValue


class Entry(BaseModel):
    id: str
    changes: list[Change]


class WebhookEvent(BaseModel):
    """Top-level webhook payload."""

    object: Literal["whatsapp_business_account"]
    entry: list[Entry]


class WebhookVerificationResponse(BaseModel):
    """Response returned to Meta for webhook verification."""

    hub_challenge: str


