from datetime import datetime, timezone

from ..schemas.interactions import (
    InteractionPayloadLocation,
    InteractionPayloadText,
    InteractionRequest,
)
from ..schemas.webhook import Message


class MessageProcessor:
    """Normalize WhatsApp messages into Terranote core interactions."""

    def __init__(self, channel: str = "whatsapp") -> None:
        self._channel = channel

    def to_interaction(self, user_id: str, message: Message) -> InteractionRequest:
        """Convert an incoming WhatsApp message into an interaction payload."""
        sent_at = self._parse_timestamp(message.timestamp)

        if message.type == "text" and message.text:
            payload = InteractionPayloadText(text=message.text.body)
        elif message.type == "location" and message.location:
            payload = InteractionPayloadLocation(
                latitude=message.location.latitude,
                longitude=message.location.longitude,
            )
        else:
            raise ValueError(f"Unsupported message type: {message.type}")

        return InteractionRequest(
            channel=self._channel,
            user_id=user_id,
            sent_at=sent_at,
            payload=payload,
        )

    @staticmethod
    def _parse_timestamp(timestamp: datetime) -> datetime:
        """Ensure timestamps are timezone-aware in UTC."""
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)


