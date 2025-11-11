from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class NoteCreatedNotification(BaseModel):
    """Payload emitted by Terranote core when a note is created."""

    channel: str = Field(pattern="^[a-z0-9_-]+$")
    user_id: str
    note_url: HttpUrl
    note_id: str
    latitude: float
    longitude: float
    text: str
    created_at: datetime
