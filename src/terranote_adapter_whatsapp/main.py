from fastapi import FastAPI

from .routes import callbacks, health, webhook
from .settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create FastAPI application instance."""
    app = FastAPI(
        title="Terranote WhatsApp Adapter",
        version="0.1.0",
        description="Adapter for Terranote core (fase 1).",
    )

    app.include_router(health.router)
    app.include_router(callbacks.router)
    app.include_router(webhook.router)

    app.state.settings = settings or get_settings()
    return app


app = create_app()


