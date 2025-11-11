from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: Annotated[str, Field(default="development")]
    core_api_base_url: Annotated[
        AnyHttpUrl, Field(default="http://localhost:8000", alias="CORE_API_BASE_URL")
    ]
    core_api_timeout_seconds: Annotated[float, Field(default=5.0, ge=0.5, le=30.0)]
    core_api_token: Annotated[str | None, Field(default=None)]

    whatsapp_verify_token: Annotated[str, Field(default="verify-token", alias="WHATSAPP_VERIFY_TOKEN")]
    whatsapp_access_token: Annotated[str, Field(default="access-token", alias="WHATSAPP_ACCESS_TOKEN")]
    whatsapp_phone_number_id: Annotated[
        str, Field(default="phone-number-id", alias="WHATSAPP_PHONE_NUMBER_ID")
    ]
    whatsapp_api_base_url: Annotated[
        AnyHttpUrl,
        Field(default="https://graph.facebook.com/v19.0", alias="WHATSAPP_API_BASE_URL"),
    ]

    notifier_secret_token: Annotated[str | None, Field(default=None, alias="NOTIFIER_SECRET_TOKEN")]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


