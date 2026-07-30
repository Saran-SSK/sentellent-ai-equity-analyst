from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    project_name: str = Field(
        default="Sentellent AI Equity Analyst",
        alias="PROJECT_NAME",
    )
    api_version: str = Field(
        default="v1",
        alias="API_VERSION",
    )
    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL",
    )

    gemini_api_key: str | None = Field(
        default=None,
        alias="GEMINI_API_KEY",
    )
    openai_api_key: str | None = Field(
        default=None,
        alias="OPENAI_API_KEY",
    )

    finnhub_api_key: str = Field(
        alias="FINNHUB_API_KEY",
    )

    alpha_vantage_api_key: str = Field(
        alias="ALPHA_VANTAGE_API_KEY",
    )

    secret_key: str = Field(
        default="change-me-in-production",
        alias="SECRET_KEY",
    )

    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
    )


settings = Settings()
