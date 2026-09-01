import pytest

from tradeos.config import Settings


def test_defaults_are_safe_for_development() -> None:
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url is None
    assert settings.redis_url is None


def test_environment_values_are_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRADEOS_ENV", "paper")
    monkeypatch.setenv("TRADEOS_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("TRADEOS_DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("TRADEOS_REDIS_URL", "redis://example")

    settings = Settings.from_environment()

    assert settings.app_env == "paper"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://example"
    assert settings.redis_url == "redis://example"


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported TRADEOS_ENV"):
        Settings(app_env="unknown").validate()


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported TRADEOS_LOG_LEVEL"):
        Settings(log_level="TRACE").validate()


def test_live_mode_is_not_enabled_by_foundation() -> None:
    with pytest.raises(ValueError, match="Live mode is not enabled"):
        Settings(app_env="live").validate()
