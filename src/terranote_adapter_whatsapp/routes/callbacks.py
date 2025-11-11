from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ..schemas.notifications import NoteCreatedNotification
from ..settings import Settings, get_settings

router = APIRouter(prefix="/callbacks", tags=["callbacks"])


@router.post(
    "/note-created",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive note creation events from Terranote core",
)
async def note_created_callback(
    notification: NoteCreatedNotification,
    request: Request,
    settings: Settings = Depends(get_settings),
    x_terranote_signature: str | None = Header(default=None, convert_underscores=False),
) -> dict[str, str]:
    """Handle note created callbacks to notify WhatsApp users."""
    if settings.notifier_secret_token and settings.notifier_secret_token != x_terranote_signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    request.app.state  # placeholder reference for future notifier dispatch
    # TODO: Implement forwarding logic to WhatsApp client.
    return {"status": "accepted"}


