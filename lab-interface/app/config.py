from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    eve_ng_base_url: str = "https://eve-ng"
    eve_ng_username: str = "admin"
    eve_ng_password: str = "eve"
    eve_ng_verify_ssl: bool = False
    eve_ng_timeout_seconds: float = 15.0


settings = Settings()
