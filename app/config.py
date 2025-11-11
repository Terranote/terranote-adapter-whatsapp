from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = Field(default="Terranote WhatsApp Adapter")
    debug: bool = Field(default=False)

    verify_token: str = Field(default="", description="Token de verificación del webhook de Meta.")
    whatsapp_token: str = Field(default="", description="Token de acceso para la WhatsApp Cloud API.")

    terranote_core_base_url: AnyHttpUrl = Field(
        default="http://localhost:8000",
        description="URL base del Terranote Core (fase 1).",
    )
    terranote_core_timeout_seconds: float = Field(default=5.0)

    notifier_secret: str = Field(
        default="",
        description="Secreto compartido para validar callbacks desde Terranote Core.",
    )

    allowed_origins: List[AnyHttpUrl] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Retorna la configuración singleton."""

    return Settings()


