from functools import lru_cache

from pydantic import Field, model_validator
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
    timesfm_model_id: str = "google/timesfm-2.5-200m-pytorch"
    timesfm_context_length: int = Field(default=1024, ge=4, le=16384)
    timesfm_horizon: int = Field(default=6, ge=4, le=8)
    timesfm_batch_size: int = Field(default=16, ge=1, le=1024)
    timesfm_device: str = "cpu"
    timesfm_timeout_seconds: int = Field(default=120, ge=1, le=1800)
    timesfm_quantile_lower_index: int = Field(default=1, ge=0, le=9)
    timesfm_quantile_upper_index: int = Field(default=9, ge=0, le=9)
    upload_directory: str = "./var/uploads"
    max_upload_bytes: int = Field(default=20 * 1024 * 1024, ge=1024)
    minimum_history_weeks: int = Field(default=12, ge=4, le=104)
    rate_limit_requests: int = Field(default=120, ge=10, le=10000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)

    @model_validator(mode="after")
    def production_secrets_are_not_defaults(self) -> "Settings":
        if self.environment.casefold() == "production":
            forbidden = {
                "development-only-change-me",
                "local-development-secret-key-please-change",
                "replace-with-at-least-32-random-characters",
            }
            if self.secret_key in forbidden or len(self.secret_key) < 32:
                raise ValueError("Production SECRET_KEY must be unique and at least 32 characters")
            if self.bootstrap_admin_password == "development-admin-only":
                raise ValueError("Development bootstrap credentials are forbidden in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
