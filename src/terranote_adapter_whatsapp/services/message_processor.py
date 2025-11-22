from datetime import datetime, timezone
from typing import Literal

from ..schemas.interactions import (
    InteractionPayload,
    InteractionPayloadLocation,
    InteractionPayloadText,
    InteractionRequest,
)
from ..schemas.webhook import Message


class MessageProcessor:
    """Normalize WhatsApp messages into Terranote core interactions."""

    def __init__(self, channel: Literal["whatsapp"] = "whatsapp") -> None:
        self._channel = channel

    def to_interaction(self, user_id: str, message: Message) -> InteractionRequest:
        """Convert an incoming WhatsApp message into an interaction payload."""
        sent_at = self._parse_timestamp(message.timestamp)

        if message.type == "text" and message.text:
            payload: InteractionPayload = InteractionPayloadText(text=message.text.body)
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
    def is_command(text: str) -> bool:
        """Check if message is a command (starts with / or is a quick reply button)."""
        if not text:
            return False
        text_stripped = text.strip()
        return text_stripped.startswith("/") or text_stripped.startswith("cmd_")

    @staticmethod
    def get_command(text: str) -> str | None:
        """Extract command from text."""
        if not MessageProcessor.is_command(text):
            return None
        text_stripped = text.strip()
        # Remove leading / or cmd_
        if text_stripped.startswith("/"):
            return text_stripped[1:].lower()
        if text_stripped.startswith("cmd_"):
            return text_stripped[4:].lower()
        return text_stripped.lower()

    @staticmethod
    def _parse_timestamp(timestamp: datetime) -> datetime:
        """Ensure timestamps are timezone-aware in UTC."""
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(timezone.utc)
