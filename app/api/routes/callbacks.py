from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import Settings, get_settings

router = APIRouter()


@router.post("/note-created")
async def note_created(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    if settings.notifier_secret:
        provided_secret = request.headers.get("x-terranote-secret")
        if not provided_secret or provided_secret != settings.notifier_secret:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret")

    payload = await request.json()
    # TODO: enviar respuesta al usuario vía WhatsApp Cloud API.
    return {"status": "received"}


