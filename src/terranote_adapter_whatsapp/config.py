 """Application configuration for the WhatsApp adapter."""
 
 from functools import lru_cache
 from typing import Literal
 
 from pydantic import AnyHttpUrl, Field, HttpUrl
 from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
 class Settings(BaseSettings):
     """Runtime configuration loaded from environment variables and `.env` files."""
 
     model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
 
     app_name: str = Field(default="Terranote WhatsApp Adapter")
     app_env: Literal["development", "production", "test"] = "development"
     log_level: Literal["debug", "info", "warning", "error", "critical"] = "info"
 
     core_api_base_url: AnyHttpUrl = Field(default="http://localhost:8000")
     core_api_timeout_seconds: float = Field(default=10.0, ge=0.1, le=60.0)
 
     whatsapp_channel_name: Literal["whatsapp"] = "whatsapp"
     whatsapp_api_base_url: HttpUrl = Field(default="https://graph.facebook.com/v21.0")
     whatsapp_access_token: str = Field(default="", min_length=0)
     whatsapp_verify_token: str = Field(default="", min_length=0)
     whatsapp_phone_number_id: str = Field(default="", min_length=0)
 
     notifier_callback_path: str = Field(default="/callbacks/note-created", min_length=1)
 
 
 @lru_cache(maxsize=1)
 def get_settings() -> Settings:
     """Return a cached settings instance."""
     return Settings()

