import json
from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Training Platform API"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://training:training@db:5432/training"
    jwt_secret_key: str = "change-me-in-development"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    auth_cookie_name: str = "training_access_token"
    auth_cookie_secure: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return [item.strip() for item in value.split(",") if item.strip()]
            if not isinstance(parsed, list):
                raise ValueError("cors_origins must be a JSON list or comma-separated string")
            return [str(item).strip() for item in parsed if str(item).strip()]
        if value is None:
            return []
        return [str(item).strip() for item in value if str(item).strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
