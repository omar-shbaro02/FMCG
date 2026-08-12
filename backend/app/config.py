from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "VAI FMCG Forecast-Augmented Growth Quality Diagnostic"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://fmcg:fmcg@localhost:5432/fmcg"
    redis_url: str = "redis://localhost:6379/0"
    frontend_url: str = "http://localhost:3000"
    secret_key: str = Field(default="development-only-change-me", min_length=16)
    access_token_minutes: int = Field(default=30, ge=5, le=1440)
    bootstrap_admin_email: str = "admin@example.com"
    bootstrap_admin_password: str = Field(default="development-admin-only", min_length=12)
    forecast_adapter: str = "mock"
    upload_directory: str = "./var/uploads"
    max_upload_bytes: int = Field(default=20 * 1024 * 1024, ge=1024)
    minimum_history_weeks: int = Field(default=12, ge=4, le=104)


@lru_cache
def get_settings() -> Settings:
    return Settings()
