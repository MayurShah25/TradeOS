"""Shared pytest configuration for TradeOS foundation tests."""

from collections.abc import Iterator

import pytest

from tradeos.config import Settings


@pytest.fixture
def test_settings() -> Iterator[Settings]:
    """Provide isolated safe configuration for tests."""
    yield Settings(app_env="test", log_level="INFO")
