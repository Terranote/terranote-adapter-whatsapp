from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    type: str
    text: MessageText | None = None
    location: MessageLocation | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(int(value), tz=timezone.utc)
        raise ValueError("Unsupported timestamp value")


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


