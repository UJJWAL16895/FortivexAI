import pytest
from pydantic import ValidationError

from src.core.settings import Settings

SENTINEL = "private-sentinel"


@pytest.fixture(autouse=True)
def isolate_config(monkeypatch):
    for field in Settings.model_fields:
        monkeypatch.delenv(field.upper(), raising=False)


def test_offline_default_has_no_secret_requirement():
    assert Settings(_env_file=None).agent_mode == "mock"


def test_live_mode_reports_fields_without_echoing_input():
    with pytest.raises(ValidationError) as failure:
        Settings(_env_file=None, agent_mode="live", gemini_api_key="private-sentinel")
    assert "GEMINI_MODEL" in str(failure.value)
    assert "private-sentinel" not in str(failure.value)


def test_configured_live_mode_hides_credentials():
    settings = Settings(
        _env_file=None,
        agent_mode="live",
        gemini_api_key=SENTINEL,
        gemini_model="catalog-primary",
        gemini_fallback_model="catalog-secondary",
    )
    assert "private-sentinel" not in repr(settings)
    assert "private-sentinel" not in settings.model_dump_json()


@pytest.mark.parametrize("key", ["", "replace_with_your_gemini_key"])
def test_live_requires_a_real_key(key):
    with pytest.raises(ValidationError, match="GEMINI_API_KEY"):
        Settings(_env_file=None, agent_mode="live", gemini_api_key=key, gemini_model="catalog-a")


def test_no_duplicate_model_in_fallback_chain():
    with pytest.raises(ValidationError, match="must differ"):
        Settings(
            _env_file=None,
            agent_mode="live",
            gemini_api_key=SENTINEL,
            gemini_model="catalog-a",
            gemini_fallback_model="catalog-a",
        )
