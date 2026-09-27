from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://lab:lab@lab-db:5432/lab"
    jwt_secret_key: str = "change-me-in-development"
    jwt_algorithm: str = "HS256"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()