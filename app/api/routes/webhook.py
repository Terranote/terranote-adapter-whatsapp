from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from app.config import Settings, get_settings
from app.services import webhook_service

router = APIRouter()


@router.get("/")
async def verify_subscription(
    hub_mode: str,
    hub_challenge: str,
    hub_verify_token: str,
    settings: Settings = Depends(get_settings),
) -> Response:
    if hub_mode != "subscribe" or hub_verify_token != settings.verify_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid verify token")

    return Response(content=hub_challenge, media_type="text/plain")


@router.post("/")
async def handle_events(
    request: Request,
    settings: Settings = Depends(get_settings),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, str]:
    payload = await request.body()

    await webhook_service.validate_signature(
        payload=payload,
        signature_header=x_hub_signature_256,
        settings=settings,
    )

    await webhook_service.process_event(payload=payload, settings=settings)
    return {"status": "accepted"}


