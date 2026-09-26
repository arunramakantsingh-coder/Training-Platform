from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Training Platform"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://training:training@db:5432/training"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
