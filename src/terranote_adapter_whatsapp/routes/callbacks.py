import httpx
import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status

from ..clients.whatsapp import WhatsAppClient
from ..schemas.notifications import NoteCreatedNotification
from ..settings import Settings, get_settings

router = APIRouter(prefix="/callbacks", tags=["callbacks"])
logger = structlog.get_logger(__name__)


@router.post(
    "/note-created",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive note creation events from Terranote core",
)
async def note_created_callback(
    notification: NoteCreatedNotification,
    settings: Settings = Depends(get_settings),
    x_terranote_signature: str | None = Header(default=None, alias="X-Terranote-Signature"),
) -> dict[str, str]:
    """Handle note created callbacks to notify WhatsApp users."""
    if settings.notifier_secret_token and settings.notifier_secret_token != x_terranote_signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    message = _format_notification(notification)
    client = WhatsAppClient(settings)

    try:
        response = await client.send_text_message(notification.user_id, message)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "whatsapp_rejected_message",
            status_code=exc.response.status_code,
            body=exc.response.text,
            user_id=notification.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="whatsapp_error",
        ) from exc
    except httpx.HTTPError as exc:
        logger.error("whatsapp_unreachable", error=str(exc), user_id=notification.user_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="whatsapp_unreachable",
        ) from exc

    logger.info(
        "notification_sent",
        user_id=notification.user_id,
        note_id=notification.note_id,
    )
    return {"status": "accepted"}


def _format_notification(notification: NoteCreatedNotification) -> str:
    return (
        f"Nota creada: {notification.note_url}\n"
        f"Lat: {notification.latitude}, Lon: {notification.longitude}\n\n"
        f"{notification.text}"
    )


