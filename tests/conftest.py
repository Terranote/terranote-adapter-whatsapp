import pytest
from fastapi.testclient import TestClient

from terranote_adapter_whatsapp.main import create_app
from terranote_adapter_whatsapp.settings import Settings, get_settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        core_api_base_url="http://localhost:8000",
        core_api_timeout_seconds=5.0,
        core_api_token=None,
        whatsapp_verify_token="verify-token",
        whatsapp_access_token="access-token",
        whatsapp_phone_number_id="phone-id",
        whatsapp_api_base_url="https://graph.facebook.com/v19.0",
        notifier_secret_token=None,
    )


@pytest.fixture
def client(settings: Settings) -> TestClient:
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)
