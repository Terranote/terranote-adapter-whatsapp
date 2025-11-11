from datetime import datetime, timezone

import pytest

from terranote_adapter_whatsapp.schemas.webhook import Message, MessageLocation, MessageText
from terranote_adapter_whatsapp.services.message_processor import MessageProcessor


def test_message_processor_converts_text_message():
    message = Message(
        id="msg-1",
        from_="123",
        timestamp=datetime(2025, 11, 11, 10, 0, tzinfo=timezone.utc),
        type="text",
        text=MessageText(body="Hola"),
    )

    interaction = MessageProcessor().to_interaction(user_id="user-1", message=message)

    assert interaction.channel == "whatsapp"
    assert interaction.user_id == "user-1"
    assert interaction.payload.type == "text"
    assert interaction.payload.text == "Hola"


def test_message_processor_converts_location_message():
    message = Message(
        id="msg-2",
        from_="123",
        timestamp=datetime(2025, 11, 11, 10, 0, tzinfo=timezone.utc),
        type="location",
        location=MessageLocation(latitude=4.61, longitude=-74.08),
    )

    interaction = MessageProcessor().to_interaction(user_id="user-1", message=message)

    assert interaction.payload.type == "location"
    assert interaction.payload.latitude == 4.61
    assert interaction.payload.longitude == -74.08


def test_message_processor_rejects_unsupported_type():
    message = Message(
        id="msg-3",
        from_="123",
        timestamp=datetime(2025, 11, 11, 10, 0, tzinfo=timezone.utc),
        type="text",
        text=None,
    )

    processor = MessageProcessor()
    with pytest.raises(ValueError):
        processor.to_interaction(user_id="user-1", message=message)
