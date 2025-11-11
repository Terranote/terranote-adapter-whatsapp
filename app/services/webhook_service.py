from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)


class SignatureValidationError(Exception):
    """Error lanzado cuando la firma del webhook no es válida."""


async def validate_signature(payload: bytes, signature_header: str | None, settings: Settings) -> None:
    """Valida la firma `X-Hub-Signature-256` según la documentación de Meta."""

    if not settings.verify_token or not settings.whatsapp_token:
        logger.warning("Verify token or WhatsApp token not configured; skipping signature validation")
        return

    if not signature_header:
        raise SignatureValidationError("Missing signature header")

    expected = hmac.new(
        key=settings.whatsapp_token.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    provided = signature_header.replace("sha256=", "")
    if not hmac.compare_digest(expected, provided):
        raise SignatureValidationError("Invalid signature")


async def process_event(payload: bytes, settings: Settings) -> None:
    """Procesa el evento JSON recibido desde Meta."""

    try:
        data: dict[str, Any] = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        logger.exception("Invalid JSON payload from Meta")
        return

    logger.debug("Incoming webhook event: %s", data)
    # TODO: normalizar mensajes y enviarlos al core en iteraciones posteriores.


