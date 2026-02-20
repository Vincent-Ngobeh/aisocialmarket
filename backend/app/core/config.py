from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "AI Social Market"
    app_version: str = "0.1.0"
    debug: bool = False

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    database_url: str = ""

    frontend_url: str = "http://localhost:5173"

    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 60

    free_tier_enabled: bool = True
    free_tier_daily_limit: int = 5

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.frontend_url.split(",")]
        if self.debug:
            origins.extend(["http://localhost:5173", "http://localhost:3000"])
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
