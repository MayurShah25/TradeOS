"""Application configuration boundary for TradeOS."""

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated, immutable runtime settings.

    Environment parsing stays at the boundary; application code receives typed values.
    Secrets are read from the environment and are never stored in source control.
    """

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str | None = None
    redis_url: str | None = None

    @classmethod
    def from_environment(cls) -> "Settings":
        """Build settings from environment variables with safe development defaults."""
        settings = cls(
            app_env=os.getenv("TRADEOS_ENV", "development"),
            log_level=os.getenv("TRADEOS_LOG_LEVEL", "INFO"),
            database_url=os.getenv("TRADEOS_DATABASE_URL"),
            redis_url=os.getenv("TRADEOS_REDIS_URL"),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        """Validate configuration invariants."""
        allowed_envs = {"development", "test", "paper", "live"}
        if self.app_env not in allowed_envs:
            raise ValueError(f"Unsupported TRADEOS_ENV: {self.app_env}")

        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in allowed_levels:
            raise ValueError(f"Unsupported TRADEOS_LOG_LEVEL: {self.log_level}")

        # Live execution configuration is intentionally not enabled by this foundation.
        # Later execution configuration must add explicit authorization and safety gates.
        if self.app_env == "live":
            raise ValueError("Live mode is not enabled by the Phase 2 foundation")
