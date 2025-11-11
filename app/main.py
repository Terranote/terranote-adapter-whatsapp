from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import callbacks, health, webhook
from app.config import get_settings


def create_app() -> FastAPI:
    """Construye la instancia de FastAPI."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
    )

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(webhook.router, prefix="/webhook", tags=["meta-webhook"])
    app.include_router(callbacks.router, prefix="/callbacks", tags=["callbacks"])

    return app


app = create_app()


