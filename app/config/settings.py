import json
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_cors_origins: list[str] = ["*"]
    app_allow_credentials: bool = False
    app_allow_methods: list[str] = ["*"]
    app_allow_headers: list[str] = ["*"]

    app_version: str = "dev"
    app_log_level: str = "INFO"

    @field_validator(
        "app_cors_origins",
        "app_allow_credentials",
        "app_allow_methods",
        "app_allow_headers",
        mode="before"
    )
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev"),
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
