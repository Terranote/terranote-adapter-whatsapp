import pytest
from fastapi.testclient import TestClient

from terranote_adapter_whatsapp.main import create_app
from terranote_adapter_whatsapp.settings import Settings, get_settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        CORE_API_BASE_URL="https://core.example.com",
        CORE_API_TIMEOUT_SECONDS=5.0,
        CORE_API_TOKEN=None,
        WHATSAPP_VERIFY_TOKEN="verify-token",
        WHATSAPP_ACCESS_TOKEN="access-token",
        WHATSAPP_PHONE_NUMBER_ID="phone-id",
        NOTIFIER_SECRET_TOKEN=None,
    )


@pytest.fixture
def client(settings: Settings) -> TestClient:
    app = create_app(settings=settings)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


