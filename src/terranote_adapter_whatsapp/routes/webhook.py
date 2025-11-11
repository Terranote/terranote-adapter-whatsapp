from fastapi import APIRouter, Depends, HTTPException, Request, Query, status

from ..schemas.webhook import WebhookEvent, WebhookVerificationResponse
from ..settings import Settings, get_settings

router = APIRouter(prefix="/webhook", tags=["whatsapp"])


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
) -> dict[str, str]:
    """Handle incoming WhatsApp events from Meta."""
    request.app.state  # placeholder to avoid unused variable warning
    settings  # placeholder until processing logic is implemented
    # TODO: Implement normalization and forwarding to Terranote core.
    return {"status": "accepted"}


