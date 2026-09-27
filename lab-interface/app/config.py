from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    lab_eve_api_url: str = "http://host.docker.internal:8300"
    lab_eve_api_verify_ssl: bool = False
    lab_eve_api_timeout_seconds: float = 15.0
    lab_eve_template_root: str = "/Training-Platform/templates"
    lab_eve_lab_root: str = "/Training-Platform"


settings = Settings()
