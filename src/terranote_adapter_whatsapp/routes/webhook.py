import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status

from ..clients.core import TerranoteCoreClient
from ..schemas.webhook import WebhookEvent, WebhookVerificationResponse
from ..services.message_processor import MessageProcessor
from ..settings import Settings, get_settings

router = APIRouter(prefix="/webhook", tags=["whatsapp"])
logger = structlog.get_logger(__name__)


@router.get(
    "",
    response_model=WebhookVerificationResponse,
    summary="WhatsApp webhook verification handshake",
)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    settings: Settings = Depends(get_settings),
) -> WebhookVerificationResponse:
    """Respond to the Facebook webhook verification challenge."""
    if hub_mode != "subscribe" or hub_verify_token != settings.whatsapp_verify_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

    return WebhookVerificationResponse(hub_challenge=hub_challenge)


@router.post("", status_code=status.HTTP_202_ACCEPTED, summary="Process WhatsApp inbound events")
async def receive_webhook(
    event: WebhookEvent,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, int | str]:
    """Handle incoming WhatsApp events from Meta."""
    processor = MessageProcessor()
    core_client = TerranoteCoreClient(settings)

    processed = 0
    for entry in event.entry:
        for change in entry.changes:
            for message in change.value.messages:
                try:
                    interaction = processor.to_interaction(user_id=message.from_, message=message)
                except ValueError as exc:
                    logger.warning(
                        "unsupported_message",
                        message_type=message.type,
                        message_id=message.id,
                        error=str(exc),
                    )
                    continue

                try:
                    response = await core_client.send_interaction(interaction)
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    logger.error(
                        "core_rejected_interaction",
                        status_code=exc.response.status_code,
                        body=exc.response.text,
                        user_id=interaction.user_id,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="core_error",
                    ) from exc
                except httpx.HTTPError as exc:
                    logger.error(
                        "core_unreachable",
                        error=str(exc),
                        user_id=interaction.user_id,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="core_unreachable",
                    ) from exc

                processed += 1
                logger.info(
                    "interaction_forwarded",
                    user_id=interaction.user_id,
                    message_id=message.id,
                )

    return {"status": "accepted", "processed": processed}


